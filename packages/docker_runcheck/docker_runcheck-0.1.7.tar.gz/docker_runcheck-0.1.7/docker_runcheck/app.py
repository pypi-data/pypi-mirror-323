from gettext import install
from typing import List
import docker
import dockerfile
import os
import tarfile
import io
from rich.console import Console
from rich.table import Table
import shutil
import typer 

app = typer.Typer()


class Binary:
    def __init__(self, name, status):
        self.name = name
        self.status = status

    def __eq__(self, other):
        """Overrides the default implementation"""
        if isinstance(other, Binary):
            return self.name == other.name and self.status == other.status
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(("name", self.name, "status", self.status))


class PackageManager:
    def __init__(self, name: str, install_cmd: str, upgrade_cmd: str, update_cmd: str):
        self.name = name
        self.install_cmd = install_cmd
        self.upgrade_cmd = upgrade_cmd
        self.update_cmd = update_cmd


def print_table(binaries):

    table = Table(title="")
    table.add_column("Binary", justify="right", no_wrap=True)
    table.add_column("Status", justify="right")
    binaries.sort(key=lambda b: b.status)
    # need to remove duplicates of binary
    # print(f"Binaries: {[(b.name, b.status) for b in  set(binaries)]}")
    for binary in set(binaries):
        table.add_row(
            "[green]" + binary.name
            if binary.status == "present"
            else "[yellow]" + binary.name
            if binary.status == "installed" or binary.status == "used before install"
            else "[red]" + binary.name,
            "[green]" + binary.status
            if binary.status == "present"
            else "[yellow]" + binary.status
            if binary.status == "installed"
            else "[red]" + binary.status,
        )

    console = Console()
    console.print(table)


# commands between EOFS are not being properly parsed

# https://stackoverflow.com/questions/39155958/how-do-i-read-a-tarfile-from-a-generator
def generator_to_stream(generator, buffer_size=io.DEFAULT_BUFFER_SIZE):
    class GeneratorStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None

        def readable(self):
            return True

        def readinto(self, b):
            try:
                l = len(b)  # : We're supposed to return at most this much
                chunk = self.leftover or next(generator)
                output, self.leftover = chunk[:l], chunk[l:]
                b[: len(output)] = output
                return len(output)
            except StopIteration:
                return 0  # : Indicate EOF

    return io.BufferedReader(GeneratorStream())


class RunChecker:

    ignore = []

    # if name of the package does not contain name of binary package
    # maybe we can have an offline list of the most common super packages
    # apk add build-base aka apt install build-essential
    # aka sudo pacman -Sy base-devel or dnf install @development-tools
    # for debian packages we might just use the api
    # get https://sources.debian.org/api/src/package-name
    # get one of the versions if not already provide with install cmd
    # in versions -> for obj in objs: obj["version"]
    # get https://sources.debian.org/api/src/cowsay/3.03+dfsg2-8/
    package_managers = [
        PackageManager(
            name="apt",
            install_cmd="install",
            upgrade_cmd="upgrade",
            update_cmd="update",
        ),
        PackageManager(
            name="apt-get",
            install_cmd="install",
            upgrade_cmd="upgrade",
            update_cmd="update",
        ),
        PackageManager(
            name="apk", install_cmd="add", upgrade_cmd="upgrade", update_cmd="update"
        ),
        PackageManager(
            name="dnf",
            install_cmd="install",
            upgrade_cmd="upgrade",
            update_cmd="check-update",
        ),
        PackageManager(
            name="pacman",
            install_cmd="-S",
            upgrade_cmd="-Syu",
            update_cmd="-Syy",
        ),
    ]

    def get_binaries(self):
        binaries = []
        for bin in self.required_binaries:
            b = Binary(bin, "missing")

            if bin in self.used_before_install:
                b = Binary(bin, "used before install")
            elif bin in [binary["name"] for binary in self.installed_binaries]:
                b = Binary(bin, "installed")
            else:
                for available_bin in self.available_binaries:
                    if bin in available_bin:
                        b = Binary(bin, "present")

            binaries.append(b)
        return binaries

    def preprocess_dockerfile(self, path_dockerfile : str):
        data = []
        with open(path_dockerfile, "r") as file:
            data = file.readlines()
            in_eof_block = False
            for i, line in enumerate(data):
                if in_eof_block:
                    data[i] = "RUN " + line
                if "<<EOF" in line:
                    # print("found EOF")
                    data[i] = ""
                    in_eof_block = True
                elif "EOF" in line:
                    data[i] = ""
                    in_eof_block = False
        with open(path_dockerfile, "w") as file:
            file.writelines(data)

    def __init__(self, path_dockerfile="./Dockerfile"):
        self.client = docker.from_env()
        self.path_dockerfile = path_dockerfile
        self.preprocess_dockerfile(path_dockerfile)
        self.commands = dockerfile.parse_file(path_dockerfile)
        self.required_binaries = []
        self.available_binaries = []
        self.used_before_install = []
        self.installed_binaries = []

    def run(self):
        self.parse_dockerfile()
        print_table(self.get_binaries())

    def update_installed_binaries(self, cmd):
        commands = []
        for command in cmd.value:
            # print(cmd)
            commands = [c.strip() for c in commands + command.split("&&")]
        for idx, command in enumerate(commands):
            cmd_parts = command.split(" ")
            pkg_manager_with_cmd = list(
                filter(lambda p: p.name == cmd_parts[0], RunChecker.package_managers)
            )
            if pkg_manager_with_cmd:
                if len(cmd_parts) > 1:
                    if cmd_parts[1] == pkg_manager_with_cmd[0].install_cmd:
                        # we found a install command
                        if len(cmd_parts) > 2:
                            self.installed_binaries.append(
                                {"name": cmd_parts[2], "command": cmd}
                            )

    def get_required_binaries(self, cmd) -> List[str]:
        commands = []
        for command in cmd.value:
            # print(cmd)
            commands = [c.strip() for c in commands + command.split("&&")]
        command_names = [c.split(" ")[0] for c in commands]

        return command_names

    def parse_dockerfile(self):
        for cmd in self.commands:
            if cmd.cmd == "RUN":
                self.required_binaries += self.get_required_binaries(cmd)
                self.update_installed_binaries(cmd)
            if cmd.cmd == "FROM":
                # print(f"FROM: {cmd.value}")
                if type(cmd.value) is tuple:
                    for i, v in enumerate(cmd.value):
                        if v.casefold() == "as":
                            if i + 1 < len(cmd.value):
                                RunChecker.ignore.append(cmd.value[i + 1])
                self.list_available_binaries(cmd)
                # just for testing the table print, we need available - required
        for installed in self.installed_binaries:
            for cmd in self.commands:
                if cmd.value[0].split(" ")[0] == installed["name"]:
                    if installed["command"].start_line > cmd.start_line:
                        self.used_before_install.append(cmd.value[0].split(" ")[0])

    def list_available_binaries(self, cmd):
        if cmd.value[0] not in RunChecker.ignore:
            images = self.client.images.list(cmd.value[0])
            for image in images:
                print(f"{image} {cmd.value[0]} is available.")
            container = None
            try:
                container = self.client.containers.create(cmd.value[0])
            except docker.errors.ImageNotFound:
                print(f"Pulling image: {cmd.value[0]}...")
                self.client.images.pull(cmd.value[0])
                container = self.client.containers.create(cmd.value[0])

            print("Created container. Analyzing contents...")

            exported = container.export()
            stream = generator_to_stream(exported)
            tar_file = tarfile.open(fileobj=stream, mode="r|*")

            # print(f"Container contents {tar_file.getnames()}")
            self.available_binaries += [p for p in tar_file.getnames() if "bin" in p]
            # print(f"Available binaries: {bin_apps}")


@app.command()
def main(file: str = typer.Option("./Dockerfile", "-f", "--file", help="Path to the Dockerfile")):
    """

    Docker RunCheck 



    This tool analyzes Dockerfiles to determine the presence and availability of various binaries.

    It helps in identifying which binaries are required, installed, or missing in the Docker image.



    Usage:

        docker_runcheck



    Options:

        -h, --help      Show this message and exit.
        -f FILE, --file FILE  Path to the Dockerfile. Default is ./Dockerfile.

    """
    run_checker = RunChecker(path_dockerfile=file)
    run_checker.run()


if __name__ == "__main__":
    app()