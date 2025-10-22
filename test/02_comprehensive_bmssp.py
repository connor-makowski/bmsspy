import time
from pamda import pamda
from scgraph import Graph
from scgraph.utils import hard_round
from scgraph.geographs.marnet import graph as marnet_graph
from scgraph.geographs.us_freeway import graph as us_freeway_graph

from scgraph_data.world_highways_and_marnet import (
    graph as world_highways_and_marnet_graph,
)

from scgraph.spanning import SpanningTree

from bmsspy.bmssp_solver import BmsspSolver
from bmsspy.solvers import bmssp

from bmsspy.helpers.utils import convert_to_constant_degree


print("\n===============\nBMSSP VS SCGraph Tests:\n===============")


def bmssp_tester(graph, origin_id, destination_id):
    obj = bmssp(graph, origin_id, destination_id)
    return {
        "path": obj["path"],
        "length": (
            hard_round(3, obj["length"]) if obj["length"] is not None else None
        ),
    }


def validate(name, realized, expected):
    # Custom lenth rounding for floating point precision issues
    if isinstance(realized, dict):
        if "length" in realized:
            realized["length"] = hard_round(3, realized["length"])
        if "path" in realized:
            realized["path"] = []
    if isinstance(expected, dict):
        if "length" in expected:
            expected["length"] = hard_round(3, expected["length"])
        if "path" in expected:
            expected["path"] = []
    if realized == expected:
        print(f"{name}: PASS")
    else:
        print(f"{name}: FAIL")
        print("Expected:", expected)
        print("Realized:", realized)

def check_correctness(name, graph, origin_id):
    graph = convert_to_constant_degree(graph)["graph"]
    bmssp_solver = BmsspSolver(graph, origin_id)
    shortest_path_tree = SpanningTree.makowskis_spanning_tree(
        graph, origin_id
    )
    validate(
        name=name,
        realized=bmssp_solver.distance_matrix,
        expected=shortest_path_tree["distance_matrix"],
    )


def time_test(name, thunk):
    start = time.time()
    thunk()
    print(f"{name}: {round((time.time()-start)*1000, 4)}ms")


graph = [
    {1: 5, 2: 1},
    {0: 5, 2: 2, 3: 1},
    {0: 1, 1: 2, 3: 4, 4: 8},
    {1: 1, 2: 4, 4: 3, 5: 6},
    {2: 8, 3: 3},
    {3: 6},
]

check_correctness(
    name="BMSSP Basic Graph Distance Matrix",
    graph=graph,
    origin_id=1,
)

check_correctness(
    name="BMSSP Marnet Graph Distance Matrix",
    graph=marnet_graph,
    origin_id=1,
)

check_correctness(
    name="BMSSP US Freeway Graph Distance Matrix",
    graph=us_freeway_graph,
    origin_id=1,
)

check_correctness(
    name="BMSSP World Highways and Marnet Graph Distance Matrix",
    graph=world_highways_and_marnet_graph,
    origin_id=1,
)

print()

graph = convert_to_constant_degree(marnet_graph)["graph"]

validate(
    name="BMSSP 1 (marnet)",
    realized=bmssp_tester(graph, 0, 5),
    expected=Graph.dijkstra_makowski(graph, 0, 5),
)

validate(
    name="BMSSP 2 (marnet)",
    realized=bmssp_tester(graph, 100, 7999),
    expected=Graph.dijkstra_makowski(graph, 100, 7999),
)

validate(
    name="BMSSP 3 (marnet)",
    realized=bmssp_tester(graph, 4022, 8342),
    expected=Graph.dijkstra_makowski(graph, 4022, 8342),
)


graph = convert_to_constant_degree(us_freeway_graph)["graph"]
validate(
    name="BMSSP 4 (us_freeway)",
    realized=bmssp_tester(graph, 0, 5),
    expected=Graph.dijkstra_makowski(graph, 0, 5),
)

validate(
    name="BMSSP 5 (us_freeway)",
    realized=bmssp_tester(graph, 4022, 8342),
    expected=Graph.dijkstra_makowski(graph, 4022, 8342),
)


graph = convert_to_constant_degree(world_highways_and_marnet_graph)["graph"]
validate(
    name="BMSSP 6 (world_highways_and_marnet)",
    realized=bmssp_tester(graph, 0, 5),
    expected=Graph.dijkstra_makowski(graph, 0, 5),
)

print("\n===============\nBMSSP Time Tests:\n===============")

time_test(
    "BMSSP 1 (marnet)",
    pamda.thunkify(bmssp_tester)(
        graph=marnet_graph, origin_id=0, destination_id=5
    ),
)
time_test(
    "BMSSP 2 (marnet)",
    pamda.thunkify(bmssp_tester)(
        graph=marnet_graph, origin_id=100, destination_id=7999
    ),
)
time_test(
    "BMSSP 3 (marnet)",
    pamda.thunkify(bmssp_tester)(
        graph=marnet_graph, origin_id=4022, destination_id=8342
    ),
)

time_test(
    "BMSSP 4 (us_freeway)",
    pamda.thunkify(bmssp_tester)(
        graph=us_freeway_graph, origin_id=0, destination_id=5
    ),
)

time_test(
    "BMSSP 5 (us_freeway)",
    pamda.thunkify(bmssp_tester)(
        graph=us_freeway_graph, origin_id=4022, destination_id=8342
    ),
)

time_test(
    "BMSSP 6 (world_highways_and_marnet)",
    pamda.thunkify(bmssp_tester)(
        graph=world_highways_and_marnet_graph, origin_id=0, destination_id=5
    ),
)

time_test(
    "Shortest Path Tree Comparison (marnet)",
    pamda.thunkify(SpanningTree.makowskis_spanning_tree)(
        graph=marnet_graph, node_id=0
    ),
)

time_test(
    "Shortest Path Tree Comparison (us_freeway)",
    pamda.thunkify(SpanningTree.makowskis_spanning_tree)(
        graph=us_freeway_graph, node_id=0
    ),
)

time_test(
    "Shortest Path Tree Comparison (world_highways)",
    pamda.thunkify(SpanningTree.makowskis_spanning_tree)(
        graph=world_highways_and_marnet_graph, node_id=0
    ),
)
