# Instructions for running neo4j accelerator demo

The collection of jupyter notebooks in this directory contain all that is need to explore using [Trovares xGT](http://www.trovares.com) as an accelerator for neo4j users.

The easiest way to do this is to clone this github repo into the linux or virtual linux environment that will run these notebooks.

## Platform Requirements

The platform to run this demo must provide these minimal features:

  - There must be x86 compute cores on this system.
    This means the demo will not run on M1-chip Macbook systems or on ARM-based cloud instances.
  - There must be a python application available to run the jupyter notebook server.
    The version of Python must be 3.6 or later.
  - There must be support for running docker containers on the platform.

### Windows

On windows systems, the requirements are that you have WSL2 enabled, some installation of linux as a WSL2 subsystem, and have [docker desktop](http://www.docker.com) installed.

### Mac OS

You must have [docker desktop](http://www.docker.com) installed as well as a Python.

### Linux

You must have a docker daemon installed and a Python version 3.6 or later.

# Launching the Jupyter Notebooks

The *jupyter notebook server* must run on the same platform as the [neo4j](http://www.neo4j.com) docker container and the [Trovares xGT}](http://www.trovares.com) docker container.  

In many situations, this means that the jupyter notebook server must run on a different system than the browser (jupyter notebook client).

The easiest way to accomplish this is to run an [ssh](https://www.openssh.com) tunnel between the client (browser) and server platforms.

![Running Jupyter Notebooks](jupyter_layout.png)