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

The *jupyter notebook server* must run on the same platform as the [neo4j](http://www.neo4j.com) docker container and the [Trovares xGT](http://www.trovares.com) docker container.

## Windows

To set up this client/server with tunneling, open a shell prompt within the Linux platform installed inside WSL2.  This must be the same Linux installation that runs docker.

After cloning this repo from the shell prompt, navigate to the directory holding these notebooks and launch:

```
$ jupyter-notebook --no-browser
```

There will be some output shown in the shell window, something like:

```
  .
  .
Or copy and paste one of these URLs:
    http://localhost:8888/?token=629af6a880bf631170846cda41c3fd475e3e77ff2d19211e
  .
  .
```

You need to copy the url (in this case, `http://localhost:8888/?token=629af6a880bf631170846cda41c3fd475e3e77ff2d19211e`) and paste it into a browser in your windows environment.

## Local Mac OS or Linux

After cloning this repo, simply navigate your Terminal shell to the directory holding these notebooks and launch:

```
$ jupyter-notebook
```

## Remote (cloud)

If you want to run the server on some remote system such as a cloud instance, you will need to launch the jupyter notebook server on the remote instance, and run the jupyter notebook client in a browser on your local system such as a laptop.

The easiest way to accomplish this is to run an [ssh](https://www.openssh.com) tunnel between the client (browser) and remote server platform.

![Running Jupyter Notebooks](jupyter_layout.png)

To do this, you must have a shell or terminal window on you local system from which you can perform an `ssh` connection.  On windows, this can be a terminal window, a powershell window, or a Linux shell window if you have a Linux installed within WSL2.

From the window, do this command:

```
$ ssh -L 8888:localhost:8888 <remote_host_name>
```

After connecting to the remote system, navigate to the directory where these notebooks have been copied (which can easily be done by cloning this github repo on the remote system) and launch the jupyter notebook server:

```
$ jupyter-notebook --no-browser
```

There will be some output shown in the remote terminal window, something like:

```
  .
  .
Or copy and paste one of these URLs:
    http://localhost:8888/?token=629af6a880bf631170846cda41c3fd475e3e77ff2d19211e
  .
  .
```

You need to copy the url (in this case, `http://localhost:8888/?token=629af6a880bf631170846cda41c3fd475e3e77ff2d19211e`) and paste it into a browser in your local environment.

Since you have established the `ssh` tunnel, the browser works as if the jupyter notebook server is local, and all communication between jupyter notebook client and server are sent between the two systems over an encrypted link.

# Running the demo

The graph data used in these notebooks contain a single vertex type with only one attribute called `id` and one edge type with a `source` and `target` attribute indicating the two endpoints of the edge and an additional attribute called `timestamp` that is stored internally as an integer (think [Unix Epoch Time](https://en.wikipedia.org/wiki/Unix_time)).

For each synthetic dataset, the size is considered the number of edges, and the number of nodes or vertices is about 1 for every 10 edges.
For example, the dataset with 1 billion edges has around 100 million nodes.

There are several dataset sizes pre-canned among the suite of notebooks.
The notebook name begins with the size (number of edges); and there are two notebooks for each size.

## The `X_setup` notebook

This notebook, for each dataset size `X`, sets up a location on the server for storing all of the data in neo4j as well as the neo4j plugins needed for this demo.
Running this notebook results in a neo4j docker image to be pulled on to the server, a host filesystem directory structure getting set up with required plugins and the select dataset, neo4j ingesting this data using the fastest `neo4j_admin import ...` method, along with installing an xGT docker image.

After completing the `X_setup` notebook, there are two docker containers running---`neo4j` and `xGT`---with data loaded into `neo4j`.
These containers have exposed ports that enable the jupyter notebook environment to interact with them.

## The `query` notebook

Once the dataset has been setup in a running `neo4j` and an `xGT` is launched and ready, the `query` notebook can be run.
This notebook connects to `neo4j` using the [Neo4j Python Driver](https://neo4j.com/docs/api/python-driver/current/index.html), connects to the `neo4j-arrow` plugin, and connects to the running `xGT` server.
There is logic in a Python function that coordinates the copying of data from `neo4j` into `xGT`.
Finally, there are two queries included in this notebook that can be run directly on `neo4j` or on the `xGT` server after invoking the `arrow flight` plugin to transfer the data.
