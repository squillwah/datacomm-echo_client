# Technical Manual: Data Comm Echo Client

## Overview

### Description

The data comm echo client is a  Python-based network communication application designed to connect to a TCP server and exchange messages using the socket library. This program demonstrates fundamental client–server communication principles where the client sends messages and the server echoes them back.

#### Source files

- ```client.py```
  - Defines the client data and functionality
- ```commands.py```
  - Defines commands to interact with the client
- ```messages.py```
  - Defines a message and procedures to work with them
- ```run.py```
  - Basic script which creates a client and starts a command input loop
- ```sock.py```
  - Defines a class to manage socket connections

### Installation

To run our client, download **all five** of the python files and place them in the **same directory**. Afterwards, use python to execute the **``run.py``** script in your terminal.

#### Requirements

- **Python 3.13.7+**
  - Our client was written and tested on **Python 3.13.7**. Other versions may work, but some *(below 3.10)* definitely won't.
- **Socket, Enum, & Dataclass Python Libraries**
  - These should come bundled with your installation of python.
- **A TCP Echo Server**
  - Our client works best with a server mimicking the functionality of the echo server running on draco1. Establishing connections to other servers over TCP is possible, but subject to hangs if they behave unexpectedly.

#### Downloading the files


### Running the program


## How to use


### Running


