# Local Search Solver (Python)

A solver based on local search.

This is the Python3 version of the C++ package [fontanf/localsearchsolver](https://github.com/fontanf/localsearchsolver).

## Description

The goal of this repository is to provide a simple framework to quickly implement algorithms based on local search.

Solving a problem only requires a couple hundred lines of code (see examples).

Algorithms:
* Restarting Local Search `restarting_local_search`
* Iterated Local Search `iterated_local_search`

## Examples

[Travelling Salesman Problem](examples/travellingsalesman.py)

## Usage, running examples from command line

Install
```shell
pip3 install localsearchsolverpy
```

Running an example:
```shell
mkdir -p data/travellingsalesman/instance
python3 -m examples.travellingsalesman -a generator -i data/travellingsalesman/instance
python3 -m examples.travellingsalesman -a restarting_local_search -i data/travellingsalesman/instance_50.json
python3 -m examples.travellingsalesman -a iterated_local_search -i data/travellingsalesman/instance_50.json
```

Update:
```shell
pip3 install --upgrade localsearchsolverpy
```

## Usage, Python library

See examples.

