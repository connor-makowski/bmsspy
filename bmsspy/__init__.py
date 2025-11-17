"""
# BMSSPy
[![PyPI version](https://badge.fury.io/py/bmsspy.svg)](https://badge.fury.io/py/bmsspy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- [![PyPI Downloads](https://img.shields.io/pypi/dm/bmsspy.svg?label=PyPI%20downloads)](https://pypi.org/project/bmsspy/) -->

A pure python bmssp implementation.

# Setup

Make sure you have Python 3.11.x (or higher) installed on your system. You can download it [here](https://www.python.org/downloads/).

### Installation

```
pip install bmsspy
```

### Documentation

- Github: https://github.com/connor-makowski/bmsspy
- Docs: https://connor-makowski.github.io/bmsspy/bmsspy.html

### Use

The example use cases in this section are based on the following graph:

![readme_graph](https://raw.githubusercontent.com/connor-makowski/bmsspy/main/static/readme_graph.png)

```python
from bmsspy import Bmssp

# Graph with 5 nodes: 0..4
# Adjacency-list representation with nonnegative weights
graph = [
    {1: 1, 2: 1},   # 0 -> 1 (1), 0 -> 2 (1)
    {2: 1, 3: 3},   # 1 -> 2 (1), 1 -> 3 (3)
    {3: 1, 4: 2},   # 2 -> 3 (1), 2 -> 4 (2)
    {4: 2},         # 3 -> 4 (2)
    {}              # 4 has no outgoing edges
]

bmssp_graph = Bmssp(graph) # Initialize the graph as a Bmssp graph

# Distances and predecessors from origin 0
res_0 = bmssp_graph.solve(origin_id=0)
print(res_0) #=>
# {
#     'origin_id': 0,
#     'destination_id': None,
#     'predecessor': [-1, 0, 0, 2, 2],
#     'distance_matrix': [0.0, 1.0, 1.0, 2.0, 3.0],
#     'path': None,
#     'length': None
# }

# Shortest path from 0 to 4
res_0_4 = bmssp_graph.solve(origin_id=0, destination_id=4)
print(res_0_4) #=>
# {
#     'origin_id': 0,
#     'destination_id': 4,
#     'predecessor': [-1, 0, 0, 2, 2],
#     'distance_matrix': [0.0, 1.0, 1.0, 2.0, 3.0],
#     'path': [0, 2, 4],
#     'length': 3
# }
```

In the example above, we only use a single orign, however multiple origins are supported if passed as a set:

```python
# Pass orgin_id as a set of ids
res_02 = bmssp_graph.solve(origin_id={0,2})
print(res_02) #=>
# {
#     'origin_id': [0, 2], 
#     'destination_id': None, 
#     'predecessor': [-1, 0, -1, 2, 2], 
#     'distance_matrix': [0.0, 1.0, 0.0, 1.0, 2.0], 
#     'path': None, 
#     'length': None
# }
```

By default graphs that are given are converted to constant degree such that worst case asymtotic run times are based on the constant degree converted graphs. Before returning a result, the constant degree conversion is undone such that the results are in the original passed graph format.

Most real world graphs are not constant degree. Converting to constant degree graphs can add substantial operational overhead during pre and post processing as well as during the actual algorithmic runtime.

To skip the constant degree conversion:
```python
# Set use_constant_degree_graph=False
bmssp_graph = Bmssp(graph=graph, use_constant_degree_graph=False)
```



## Development

To avoid extra development overhead, we expect all developers to use a unix based environment (Linux or Mac). If you use Windows, please use WSL2.

For development, we test using Docker so we can lock system deps and swap out python versions easily. However, you can also use a virtual environment if you prefer. We provide a test script and a prettify script to help with development.

### Making Changes

1) Fork the repo and clone it locally.
2) Make your modifications.
3) Use Docker or a virtual environment to run tests and make sure they pass.
4) Prettify your code.
5) **DO NOT GENERATE DOCS**.
    - We will generate the docs and update the version number when we are ready to release a new version.
6) Only commit relevant changes and add clear commit messages.
    - Atomic commits are preferred.
7) Submit a pull request.

### Docker

Make sure Docker is installed and running.

- Create a docker container and drop into a shell
    - `./run.sh`
- Run all tests (see ./utils/test.sh)
    - `./run.sh test`
- Prettify the code (see ./utils/prettify.sh)
    - `./run.sh prettify`

- Note: You can and should modify the `Dockerfile` to test different python versions.

### Virtual Environment

- Create a virtual environment
    - `python3.XX -m venv venv`
        - Replace `3.XX` with your python version (3.11 or higher)
- Activate the virtual environment
    - `source venv/bin/activate`
- Install the development requirements
    - `pip install -r requirements/dev.txt`
- Run Tests
    - `./utils/test.sh`
- Prettify Code
    - `./utils/prettify.sh`"""

from bmsspy.entrypoint import Bmssp
