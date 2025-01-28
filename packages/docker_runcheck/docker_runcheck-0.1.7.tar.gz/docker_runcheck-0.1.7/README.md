
<a name="readme-top"></a>


<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!--[![Issues][issues-shield]][issues-url]
[![LinkedIn][linkedin-shield]][linkedin-url]-->



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/pfaaj/docker-runcheck">
    <img src="images/logo.png" alt="Logo" width="300" height="300">
  </a>

  <h3 align="center">Docker runcheck</h3>

  <p align="center">
    Check wheter required binaries are available in the used docker image without having to first run an expensive and long docker build.
    <br />
    ·
    <a href="https://github.com/pfaaj/docker-runcheck/issues">Report Bug</a>
    ·
    <a href="https://github.com/pfaaj/docker-runcheck/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

+ Run docker-runcheck to validate your Dockerfile before attempting time-intensive docker builds. 

+ docker-runcheck works as follows:
  + looks for a file name Dockerfile in the current working directory
  + contructs one or more containers based on the mentioned parent image
  + docker image is downloaded if not present
  but it is not built.
  + export image as tar file and compile a list of the available binaries in the image
  + compile a list of any binaries mentioned in a RUN command that are  missing from the image or are used before being installed by a package manager.

</br>


<!-- GETTING STARTED -->
## Getting Started


```
pip install docker_runcheck
```



<!-- USAGE EXAMPLES -->

### Usage

You can then run docker-runcheck with:

  ```sh
  python -m docker_runcheck
  ```

![](images/runcheck.gif)





<!-- ROADMAP -->
## Roadmap

- [] Detect binary is installed by super package (e.g. build-essential)


<!--See the [open issues](https://github.com/pfaaj/docker-runcheck/issues) for a full list of proposed features (and known issues).-->


<!-- For apt stuff, package info

git clone https://salsa.debian.org/apt-team/python-apt
cd python-apt
sudo apt install libapt-pkg-dev
python setup.py build

or alternatively https://help.launchpad.net/API/launchpadlib

or https://sources.debian.org/doc/api/ -> examples 
https://sources.debian.org/api/info/package/davfs2/1.5.2-1/ 
https://sources.debian.org/api/src/cowsay/3.03+dfsg1-4/cows/
-->

 
## Contributing

Contributions are **greatly appreciated**.

If you have a suggestion to make this project better, please fork the repo and create a pull request. 
Don't forget to give the project a star! Thanks!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/SuperAmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some Super Amazing Feature'`)
4. Push to the Branch (`git push origin feature/SuperAmazingFeature`)
5. Open a Pull Request

</br>

<!-- LICENSE -->
## License

Distributed under the MIT License. 


</br>


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS 
## Acknowledgments


<p align="right">(<a href="#readme-top">back to top</a>)</p>
-->


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/pfaaj/docker-runcheck.svg?style=for-the-badge
[contributors-url]: https://github.com/pfaaj/docker-runcheck/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/pfaaj/docker-runcheck.svg?style=for-the-badge
[forks-url]: https://github.com/pfaaj/docker-runcheck/network/members
[stars-shield]: https://img.shields.io/github/stars/pfaaj/docker-runcheck.svg?style=for-the-badge
[stars-url]: https://github.com/pfaaj/docker-runcheck/stargazers
[issues-shield]: https://img.shields.io/github/issues/pfaaj/docker-runcheck.svg?style=for-the-badge
[issues-url]: https://github.com/pfaaj/docker-runcheck/issues
[license-shield]: https://img.shields.io/github/license/pfaaj/docker-runcheck.svg?style=for-the-badge
[license-url]: https://github.com/pfaaj/docker-runcheck/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/paulo-aragao
[product-screenshot]: images/screenshot.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
