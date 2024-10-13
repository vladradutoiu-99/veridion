# Prereq

- Docker
- docker-compose
- Python

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.

```bash
pip install -r requirements.txt
```

Copy docai folder from memory_leaks folder to memory_leaks/worker folder.

## Usage

Making changes to the application would require stopping the process and re-running the starting command.

Start the container:

```bash
docker-compose up --build
```

Check container resources:
```bash
docker stats
```

Call the endpoint:
curl -X POST --header "Content-Type: application/json" --data @body.json http://localhost:8080/process

Solution:
The only really reliable way to ensure that a large but temporary use of memory DOES return all resources to the system when it's done, is to have that use happen in a subprocess, which does the memory-hungry work then terminates. Under such conditions, the operating system WILL do its job, and gladly recycle all the resources the subprocess may have gobbled up. Fortunately, the multiprocessing module makes this kind of operation (which used to be rather a pain) not too bad in modern versions of Python.
