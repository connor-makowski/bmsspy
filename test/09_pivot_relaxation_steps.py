# Regression test for a frontier-aliasing bug in BmsspCore.find_pivots that
# made results incorrect for pivot_relaxation_steps (k) >= 3. Correctness of
# BMSSP does not depend on k (larger k only trades off running time), so every
# k >= 1 must return the same, correct distances.

from scgraph.spanning import SpanningTree
from scgraph.utils import hard_round

from bmsspy import Bmssp

print("\n===============\nPivot Relaxation Steps (k) Tests:\n===============")

failed = False


def eq(a, b):
    fa, fb = float(a), float(b)
    if fa == float("inf") or fb == float("inf"):
        return fa == fb
    return hard_round(6, fa) == hard_round(6, fb)


# Minimal reproduction: a 4-node path. With the bug, k>=3 returned
# [0, 1, inf, inf] because relaxation stopped after the first step.
path_graph = [{1: 1}, {2: 1}, {3: 1}, {}]
for k in [1, 2, 3, 4, 5]:
    dm = Bmssp(path_graph, use_constant_degree_graph=False).solve(
        origin_id=0, pivot_relaxation_steps=k
    )["distance_matrix"]
    if dm == [0, 1, 2, 3]:
        print(f"Path Graph k={k}: PASS")
    else:
        failed = True
        print(f"Path Graph k={k}: FAIL ({dm})")


# A real graph, checked against a Dijkstra reference across several k values.
from scgraph.geographs.us_freeway import graph as us_freeway_graph

expected = SpanningTree.makowskis_spanning_tree(us_freeway_graph, 1)[
    "distance_matrix"
][: len(us_freeway_graph)]
for k in [2, 3, 4, 6]:
    dm = Bmssp(us_freeway_graph, use_constant_degree_graph=False).solve(
        origin_id=1, pivot_relaxation_steps=k
    )["distance_matrix"]
    if all(eq(a, b) for a, b in zip(dm, expected)):
        print(f"US Freeway k={k}: PASS")
    else:
        failed = True
        print(f"US Freeway k={k}: FAIL")


if failed:
    raise Exception("Pivot Relaxation Steps (k) test failed")
