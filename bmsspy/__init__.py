r"""
# BMSSPy
[![PyPI version](https://badge.fury.io/py/bmsspy.svg)](https://badge.fury.io/py/bmsspy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/badge/bmsspy)](https://pepy.tech/project/bmsspy/)

**A high-performance Python and C++ implementation of the Bounded Multi-Source Shortest Path (BMSSP) algorithm.**

BMSSPy implements the Bounded Multi-Source Shortest Path (BMSSP) algorithm ([Duan et al., 2025](https://arxiv.org/abs/2504.17033)), breaking Dijkstra's long-standing sorting barrier for shortest paths on directed graphs. It provides both an accessible pure-Python implementation and an optimized C++ extension powered by nanobind. BMSSPy supports single-source shortest paths (SSSP), multi-source shortest paths (MSSP), point-to-point queries, predecessor tree extraction, and optional constant-degree graph transformations.

- **Docs**: https://connor-makowski.github.io/bmsspy/bmsspy.html
- **GitHub**: https://github.com/connor-makowski/bmsspy
- **Bmsspy Paper**: https://ssrn.com/abstract=5777186
- **Original Algorithm Paper**: https://arxiv.org/abs/2504.17033

---

## Citation

If you use BMSSPy in your research, please cite:

> Makowski, Connor and Guter, Willem and Russell, Tim and Saragih, Austin, BMSSPy: A Python Package and Empirical Comparison of Bounded Multi-Source Shortest Path Algorithm (November 19, 2025). MIT Center for Transportation & Logistics Research Paper No. 2025/034, Available at SSRN: https://ssrn.com/abstract=5777186

```bibtex
@article{makowski2025bmsspy,
  title={BMSSPy: A Python Package and Empirical Comparison of Bounded Multi-Source Shortest Path Algorithm},
  author={Makowski, Connor and Guter, Willem and Russell, Tim and Saragih, Austin},
  journal={MIT Center for Transportation & Logistics Research Paper Series},
  number={2025-034},
  year={2025},
  url={https://ssrn.com/abstract=5777186}
}
```

---

## Installation

Make sure you have Python 3.11 or higher installed.

```bash
pip install bmsspy
```

Pre-built binary wheels with C++ acceleration are provided for Linux, macOS, and Windows.

### Pure Python Installation (Skip Binary Builds)

If you want to install `bmsspy` in pure Python mode without compiling or using binary extensions (or in environments without a C++ compiler):

- **Linux / macOS / WSL2**:
  ```bash
  BMSSPY_NO_BUILD=1 pip install --no-binary bmsspy bmsspy
  ```
  Or with `uv`:
  ```bash
  BMSSPY_NO_BUILD=1 uv pip install --no-binary bmsspy bmsspy
  ```

- **Windows (PowerShell)**:
  ```powershell
  $env:BMSSPY_NO_BUILD="1"
  pip install --no-binary bmsspy bmsspy
  ```

- **Windows (CMD)**:
  ```cmd
  set BMSSPY_NO_BUILD=1
  pip install --no-binary bmsspy bmsspy
  ```

#### Verifying Backend
Check whether C++ acceleration or the pure Python backend is active:

```python
from bmsspy import has_cpp
print(has_cpp())  # True if compiled C++ extension is loaded, False otherwise
```

---

## Quick Start

Solve single-source and point-to-point shortest paths on a directed weighted graph:

![readme_graph](https://raw.githubusercontent.com/connor-makowski/bmsspy/main/static/readme_graph.png)

```python
from bmsspy import Bmssp, BmsspC, has_cpp

# Directed graph with 5 nodes (0..4) represented as an adjacency list of dicts:
graph = [
    {1: 1, 2: 1},   # 0 -> 1 (w=1), 0 -> 2 (w=1)
    {2: 1, 3: 3},   # 1 -> 2 (w=1), 1 -> 3 (w=3)
    {3: 1, 4: 2},   # 2 -> 3 (w=1), 2 -> 4 (w=2)
    {4: 2},         # 3 -> 4 (w=2)
    {},             # 4 has no outgoing edges
]

# Use C++ acceleration if available, otherwise pure Python:
solver_cls = BmsspC if has_cpp() else Bmssp
solver = solver_cls(graph)

# Single-source shortest path from origin 0:
res = solver.solve(origin_id=0)
print(res["distance_matrix"])  #=> [0.0, 1.0, 1.0, 2.0, 3.0]
print(res["predecessor"])      #=> [-1, 0, 0, 2, 2]

# Point-to-point shortest path from 0 to 4:
res_p2p = solver.solve(origin_id=0, destination_id=4)
print(res_p2p["path"])    #=> [0, 2, 4]
print(res_p2p["length"])  #=> 3.0
```

### Result Dictionary Structure

The `.solve()` method returns a dictionary with the following keys:

| Key | Description |
|---|---|
| `origin_id` | Origin node ID (or list of origin IDs if a set was supplied) |
| `destination_id` | Destination node ID, or `None` if calculating the full shortest path tree |
| `distance_matrix` | List of shortest path distances from origin(s) to every node in the graph |
| `predecessor` | Predecessor list where `predecessor[i]` is the node visited immediately before `i` |
| `path` | Reconstructed shortest path `[origin, ..., destination]`, or `None` if `destination_id` was not provided |
| `length` | Total distance along the shortest path to `destination_id`, or `None` if `destination_id` was not provided |

---

# Core Concepts

## Graph Structure

Graphs are represented as zero-indexed adjacency lists (a Python list of dictionaries):

```python
graph = [
    {1: 5.0, 2: 1.2},   # Node 0 connects to node 1 (weight 5.0) and node 2 (weight 1.2)
    {0: 5.0, 2: 2.1},   # Node 1 connects to node 0 and node 2
    {0: 1.2, 1: 2.1},   # Node 2 connects to node 0 and node 1
]
```

- Each index in the list corresponds to a node ID (`0` to `n - 1`).
- Each dictionary maps neighbor IDs to non-negative edge weights (integer or float).

---

# Usage Guide

## Solvers: C++ vs Pure Python

BMSSPy provides two solver implementations that share an identical interface:

| Solver | Backend | Description |
|---|---|---|
| `BmsspC` | C++20 (`nanobind`) | Highly optimized native implementation for maximum performance on production workloads and benchmarks. |
| `Bmssp` | Pure Python | Reference implementation with zero binary dependencies, ideal for inspection, debugging, and environments without C++ toolchains. |

```python
from bmsspy import Bmssp, BmsspC, has_cpp

# Instantiate whichever solver suits your environment:
if has_cpp():
    solver = BmsspC(graph)
else:
    solver = Bmssp(graph)
```

## Multi-Source Shortest Path (MSSP)

Pass a set of node IDs to `origin_id` to compute shortest paths originating simultaneously from multiple source vertices:

```python
solver = Bmssp(graph)

# Compute distances from origin set {0, 2}
res = solver.solve(origin_id={0, 2})

print(res["origin_id"])        #=> [0, 2]
print(res["distance_matrix"])  #=> [0.0, 1.0, 0.0, 1.0, 2.0]
print(res["predecessor"])      #=> [-1, 0, -1, 2, 2]
```

## Constant-Degree Graph Conversion

The theoretical asymptotic complexity of BMSSP assumes the graph has bounded degree (constant maximum degree $\le 2$). By default, BMSSPy automatically transforms arbitrary-degree graphs into constant-degree graphs, runs the algorithm, and projects the resulting distances and predecessors back to the original graph structure.

Most real-world networks are not constant-degree, and the conversion phase can introduce operational overhead. You can configure or disable this behavior via `use_constant_degree_graph`:

```python
# Skip constant-degree conversion for faster practical runtimes:
solver = Bmssp(graph=graph, use_constant_degree_graph=False)
```

### Supported Conversion Modes

| Value | Description |
|---|---|
| `True` / `'constant_degree'` / `'degree'` *(Default)* | Converts graph to constant in- and out-degree ($\le 2$ incoming and outgoing edges per node). |
| `'constant_out_degree'` / `'out_degree'` | Converts graph to constant out-degree only ($\le 2$ outgoing edges per node). |
| `False` / `None` | Disables degree conversion; runs BMSSP directly on the input graph. |

## Algorithm Parameters & Tuning

You can fine-tune the solver during initialization or at query time:

```python
solver = Bmssp(
    graph=graph,
    precision=6,                    # Decimal precision for unique path perturbations
    use_constant_degree_graph=False,
)

res = solver.solve(
    origin_id=0,
    destination_id=4,
    pivot_relaxation_steps=3,       # Custom relaxation step count k
    target_tree_depth=2,            # Custom search tree depth t
)
```

### Solver Initialization Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `graph` | `list[dict[int, int \| float]]` | *Required* | Adjacency list representation of the graph. |
| `precision` | `int` | `6` | Decimal precision for rounding edge weights. Tiny unique values are added to guarantee distinct path lengths. |
| `use_constant_degree_graph` | `bool \| str` | `True` | Strategy for constant-degree conversion (`True`, `False`, `'constant_out_degree'`). |

### `.solve()` Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `origin_id` | `int \| set[int]` | *Required* | Starting node ID, or set of IDs for multi-source routing. |
| `destination_id` | `int \| None` | `None` | Target node ID for point-to-point queries. If `None`, computes the full shortest path tree. |
| `pivot_relaxation_steps` | `int \| None` | `None` ($k \approx \lceil\log_2(n)^{1/3}\rceil$) | Number of relaxation steps to execute when identifying pivots. |
| `target_tree_depth` | `int \| None` | `None` ($t \approx \lfloor\log_2(n)^{2/3}\rfloor$) | Target depth of the search tree. |

---

# Development

For local development, we expect a Unix-based environment (Linux, macOS, or WSL2 on Windows) and use [uv](https://docs.astral.sh/uv/) for project and dependency management.

### Setup

Clone the repository and install dev dependencies:

```bash
uv sync --extra dev --reinstall
```

### Common Commands

| Command | Description |
|---|---|
| `uv run pytest` | Run all unit tests in the current virtual environment |
| `uv run pytest -v` | Run tests with verbose output |
| `uv run pytest test/01_bmssp.py` | Run a specific test file |
| `uv run nox` | Run test matrix across Python 3.11, 3.12, 3.13, 3.14, and PyPy (both C++ and pure-Python) |
| `uv run nox -s tests-3.14` | Run tests on a specific Python version |
| `uv run python utils/prettify.py` | Format code using autoflake and black |

### Making Changes

1. Fork the repository and create a feature branch.
2. Make your modifications.
3. Run tests across backends to verify functionality (`uv run pytest` or `uv run nox`).
4. Format code using `uv run python utils/prettify.py`.
5. **DO NOT GENERATE DOCS** (documentation is compiled and versioned during official releases).
6. Create atomic commits with descriptive messages and open a pull request.

---

## References

- **BMSSP Breakthrough Paper**: Duan, R., Mao, J., Shu, C., & Yin, L. (2025). *Breaking the Sorting Barrier for Shortest Paths on Directed Graphs*. [arXiv:2504.17033](https://arxiv.org/abs/2504.17033).
- **BMSSPy Empirical Study**: Makowski, C., Guter, W., Russell, T., & Saragih, A. (2025). *BMSSPy: A Python Package and Empirical Comparison of Bounded Multi-Source Shortest Path Algorithm*. MIT CTL Research Paper Series. [SSRN:5777186](https://ssrn.com/abstract=5777186).
- **SCGraph**: A Python library for shortest path routing on geographic and supply chain networks integrating BMSSPy: [scgraph](https://github.com/connor-makowski/scgraph).

"""


from bmsspy.entrypoint import Bmssp
from bmsspy.helpers.utils import has_cpp, cpp_check

try:
    from bmsspy.cpp import BmsspC
except ImportError:
    class BmsspC:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "C++ implementation 'BmsspC' is not available. Please install the C++ supported wheels or build the C++ extension."
            )


