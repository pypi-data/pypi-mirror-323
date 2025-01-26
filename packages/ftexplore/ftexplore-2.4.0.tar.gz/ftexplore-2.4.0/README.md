# ft-Explore

> ft-Explore allows to control motors and to check inputs by GUI and user-provided Python code.

<!-- <a href="https://www.henrici.name/projects/ftexplore.html"><img src="https://www.henrici.name/projects/images/ftexplore1_401.gif" title="ft-Explore GUI" alt="ft-Explore GUI"></a> -->

[![ft-Explore GUI](https://www.henrici.name/projects/images/ftexplore1.gif)](https://www.henrici.name/projects/ftexplore.html)

ft-Explore was implemented to interface with hardware of technical models for educational purposes. It is open-source and contains interface modules for widely available hardware (RaspberryPi with Adafruit Motor HAT).

---

## Features

- Graphical user interface for controlling four motors/lights and showing the state of eight digital inputs
- Platform independent, tested on Windows and Linux (Debian and Raspbian)
- No dependencies except hardware drivers when operating locally
- Controlling motors/lights and getting the state of the inputs can be done by user-provided Python scripts
- The user-provided Python scripts can be executed and interrupted in the GUI. Script output and exceptions are shown there
- Manual control via GUI and script-based control is possible simultaneously
- GUI and hardware can be distributed to multiple machines, e.g. hardware on a headless RaspberryPi can be controlled via GUI on a Windows notebook

---

## Installation

ft-Explore can be installed easily. See the sections below depending on your platform.

### Windows

- Download msi installer file (can be found "dist_msi" folder in the repository)
- Install using the msi installer
- Afterwards the application can be started via shortcut "ft-Explore" in start menu

Alternatively, you can download the source code and run it after installing Python (e.g. via https://www.anaconda.com/distribution/). See the Linux section below for required Python packages.

### Linux

- Make sure that you use Python version 3.5 or newer
- Install Python libraries as needed:

> in case the application shall not just be used locally and shall use the network

```shell
$ pip install cffi pynng
```

> in case you are running on a RaspberryPi and want to access the GPIOs as inputs

```shell
$ pip install RPi.GPIO
```

> in case you are running on a RaspberryPi with an Adafruit Motor HAT

```shell
$ pip install adafruit_motorkit
```

> in case you want to be able to watch for keyboard events

```shell
$ pip install keyboard
```

- Install ft-Explore:

```shell
$ pip install ftexplore
```

- Run ft-Explore

> run and show help page

```shell
$ python -m ftexplore --help
```

---

### Clone (for developers only)

- Clone this repo to your local machine using `https://www.hosting-srv.de/gitea/HNET/ftexplore.git`

---

## Usage

- Demo usage

> Show GUI and use no real hardware for demo purposes (the default):

```shell
$ python -m ftexplore
```

> This is equivalent to

```shell
$ python -m ftexplore --loglevel info --hardware demo
```

In this mode, there is just emulated hardware. When you control the motors, depending on the direction of the motors the inputs are set.

- Show GUI and use the locally available default hardware (Adafruit Motor HAT and eight RaspberryPi GPIOs as inputs)

```shell
$ python -m ftexplore --hardware default
```

Use this mode if you're working locally on a RaspberryPi with an Adafruit Motor HAT shield.0

- Distributed operation with local GUI and remote hardware

> Listening side with the hardware (adapt port as needed)

```shell
$ python -m ftexplore --hardware default --listen 2201
```
> Client side with the GUI (adapt IP address and port as needed)

```shell
$ python -m ftexplore --hardware 192.168.1.1:2201
```

- Show help page for details on command line arguments

```shell
$ python -m ftexplore --help
```

## Documentation

### Writing Usercode

See the separate documentation for writing usercode in the doc directory:

[Documentation on writing user code](https://www.hosting-srv.de/gitea/HNET/ftexplore/src/branch/master/doc/usercode.md)

### Source Code Organization

- src/ftexplore/eventprocessor

This folder contains code for event processing and event distribution to the applications submodules. The application works by broadcasting events between the different application modules.

- src/ftexplore/gui

This folder contains the code for the graphical user interface. That interface is based on Tk.

- src/ftexplore/hardware

This folder contains modules to communicate with different types of hardware. A special hardware is "remote" hardware that resides on another machine and is accessed via network. Adapt the demo hardware to quickly implement support for your special hardware.

- src/ftexplore/listener

This folder contains the module that provides access to the local hardware via the network. One or more clients can be connected.

- src/ftexplore/usercode 

This folder contains the code controlling the execution of user-provided code.

---

## License

[![License](http://img.shields.io/:license-gpl3-blue.svg?style=flat-square)](http://opensource.org/licenses/gpl-license.php)

- **[GPL3 license](http://opensource.org/licenses/gpl-license.php)**
- Copyright 2019-2023 <a href="https://www.henrici.name/projects/ftexplore.html" target="_blank">Dirk Henrici</a>
