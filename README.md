<div id="top"></div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/SBUNetSys/IPFS-Temporal-Script">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

<h3 align="center">IPFS Temporal Evaluation</h3>

  <p align="center">
    With this project, we aim to evaluate different aspects of IPFS via the files in the network.
    Our first task is to collect snapshots of some famous files ( CIDs ) over time.
    <br />
    <a href="https://docs.ipfs.io/"><strong>Explore the IPFS docs »</strong></a>
    <br />
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

With this project, we aim to evaluate different aspects of IPFS via the files in the network.
Our first task is to collect snapshots of some famous files ( CIDs ) over time.
<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

* [Python](https://www.python.org/)
* [Golang](https://go.dev/)
* [go-ipfs](https://github.com/ipfs/go-ipfs)

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started


### Prerequisites

* python
* golang 
* go-ipfs ( currently this binary is being fetched from a different repo, but you can install and modify to run your own changes )

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/SBUNetSys/IPFS-Temporal-Script
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

1. Create folder with the current date under results. For eg. results/2022-02-19
2. Add a file all_cid.txt which contains the CIDs separated by a new line.
3. Run the docker script ( which in turn runs the script in a container of the image created using the Dockerfile )
   ```sh
   ./docker.sh 
   ```
4. Wait for the results to be published in results/<currentDate> ( You can run docker ps to see if the container is still running )

<p align="right">(<a href="#top">back to top</a>)</p>
