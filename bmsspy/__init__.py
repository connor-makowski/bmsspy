"""
# BMSSPy
[![PyPI version](https://badge.fury.io/py/bmsspy.svg)](https://badge.fury.io/py/bmsspy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<!-- [![PyPI Downloads](https://img.shields.io/pypi/dm/bmsspy.svg?label=PyPI%20downloads)](https://pypi.org/project/bmsspy/) -->

A pure python bmssp implementation.

# Setup

Make sure you have Python 3.10.x (or higher) installed on your system. You can download it [here](https://www.python.org/downloads/).

### Installation

```
pip install bmsspy
```


### Use

```python
from bmsspy import Bmssp

graph = [
    {1: 1, 2: 1},
    {2: 1, 3: 3},
    {3: 1, 4: 2},
    {4: 2},
    {}
]

bmssp_graph = (graph) 

bmssp_graph.solve(origin_id=0) #=>
# {
#     'origin_id': 0,
#     'destination_id': None,
#     'predecessor': [-1, 0, 0, 2, 2],
#     'distance_matrix': [0, 1, 1, 2, 3],
#     'path': None,
#     'length': None
# }

bmssp_graph.solve(origin_id=0, destination_id=4) #=>
# {
#     'origin_id': 0,
#     'destination_id': 4,
#     'predecessor': [-1, 0, 0, 2, 2],
#     'distance_matrix': [0, 1, 1, 2, 3],
#     'path': [0, 2, 4],
#     'length': 3
# }
```
"""

from bmsspy.entrypoint import Bmssp
