from scgraph import GeoGraph, Graph
from scgraph.utils import hard_round
from bmsspy import Bmssp

us_freeway_graph = GeoGraph.load_geograph("us_freeway").graph


def eq(a, b):
    fa, fb = float(a), float(b)
    if fa == float("inf") or fb == float("inf"):
        return fa == fb
    return hard_round(6, fa) == hard_round(6, fb)


def test_path_graph_pivot_relaxation():
    path_graph = [{1: 1}, {2: 1}, {3: 1}, {}]
    for k in [1, 2, 3, 4, 5]:
        dm = Bmssp(path_graph, use_constant_degree_graph=False).solve(
            origin_id=0, pivot_relaxation_steps=k
        )["distance_matrix"]
        assert dm == [0, 1, 2, 3]


def test_us_freeway_pivot_relaxation():
    expected = Graph(us_freeway_graph).get_shortest_path_tree(origin_id=1)[
        "distance_matrix"
    ][: len(us_freeway_graph)]
    for k in [2, 3, 4, 6]:
        dm = Bmssp(us_freeway_graph, use_constant_degree_graph=False).solve(
            origin_id=1, pivot_relaxation_steps=k
        )["distance_matrix"]
        assert all(eq(a, b) for a, b in zip(dm, expected))


if __name__ == "__main__":
    print(
        "\n===============\nPivot Relaxation Steps (k) Tests:\n==============="
    )
    failed = False

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

    expected = Graph(us_freeway_graph).get_shortest_path_tree(origin_id=1)[
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

