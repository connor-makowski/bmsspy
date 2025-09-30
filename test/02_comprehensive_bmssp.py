import time
from pamda import pamda
from scgraph import Graph
from scgraph.utils import hard_round
from scgraph.geographs.marnet import graph as marnet_graph
from scgraph.geographs.us_freeway import graph as us_freeway_graph

from scgraph_data.world_highways_and_marnet import graph as world_highways_and_marnet_graph

from scgraph.spanning import SpanningTree

from bmsspy.bmssp_solver import BmsspSolver
from bmsspy.solvers import bmssp


print("\n===============\nBMSSP VS SCGraph Tests:\n===============")

def bmssp_tester(graph, origin_id, destination_id):
    obj = bmssp(graph, origin_id, destination_id)
    return {
        'path': obj['path'],
        'length': hard_round(3, obj['length']) if obj['length'] is not None else None,
    }


def validate(name, realized, expected):
    # Custom lenth rounding for floating point precision issues
    if isinstance(realized, dict):
        if "length" in realized:
            realized["length"] = hard_round(3, realized["length"])
    if isinstance(expected, dict):
        if "length" in expected:
            expected["length"] = hard_round(3, expected["length"])
    if realized == expected:
        print(f"{name}: PASS")
    else:
        print(f"{name}: FAIL")
        print("Expected:", expected)
        print("Realized:", realized)


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

bmssp_solver = BmsspSolver(graph, 1)
shortest_path_tree = SpanningTree.makowskis_spanning_tree(graph, 1)
validate(
    name="BMSSP Basic Graph Distance Matrix",
    realized=bmssp_solver.distance_matrix,
    expected=shortest_path_tree["distance_matrix"],
)

bmssp_marnet_solver = BmsspSolver(marnet_graph, 1)
marnet_shortest_path_tree = SpanningTree.makowskis_spanning_tree(marnet_graph, 1)
validate(
    name="BMSSP Marnet Graph Distance Matrix",
    realized=bmssp_marnet_solver.distance_matrix,
    expected=marnet_shortest_path_tree["distance_matrix"],
)

bmssp_us_freeway_solver = BmsspSolver(us_freeway_graph, 1)
us_freeway_shortest_path_tree = SpanningTree.makowskis_spanning_tree(us_freeway_graph, 1)
validate(
    name="BMSSP US Freeway Graph Distance Matrix",
    realized=bmssp_us_freeway_solver.distance_matrix,
    expected=us_freeway_shortest_path_tree["distance_matrix"],
)   

world_highways_and_marnet_solver = BmsspSolver(world_highways_and_marnet_graph, 1)
world_highways_and_marnet_shortest_path_tree = SpanningTree.makowskis_spanning_tree(world_highways_and_marnet_graph, 1)
validate(
    name="BMSSP World Highways and Marnet Graph Distance Matrix",
    realized=world_highways_and_marnet_solver.distance_matrix,
    expected=world_highways_and_marnet_shortest_path_tree["distance_matrix"],
)

print()

graph = marnet_graph

validate(
    name="BMSSP 1 (marnet)",
    realized=bmssp_tester(marnet_graph, 0, 5),
    expected=Graph.dijkstra_makowski(marnet_graph, 0, 5),
)

validate(
    name="BMSSP 2 (marnet)",
    realized=bmssp_tester(marnet_graph, 100, 7999),
    expected=Graph.dijkstra_makowski(marnet_graph, 100, 7999),
)

validate(
    name="BMSSP 3 (marnet)",
    realized=bmssp_tester(marnet_graph, 4022, 8342),
    expected=Graph.dijkstra_makowski(marnet_graph, 4022, 8342),
)

validate(
    name="BMSSP 4 (us_freeway)",
    realized=bmssp_tester(us_freeway_graph, 0, 5),
    expected=Graph.dijkstra_makowski(us_freeway_graph, 0, 5),
)

validate(
    name="BMSSP 5 (us_freeway)",
    realized=bmssp_tester(us_freeway_graph, 4022, 8342),
    expected=Graph.dijkstra_makowski(us_freeway_graph, 4022, 8342),
)

validate(
    name="BMSSP 6 (world_highways_and_marnet)",
    realized=bmssp_tester(world_highways_and_marnet_graph, 0, 5),
    expected=Graph.dijkstra_makowski(world_highways_and_marnet_graph, 0, 5),
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
        graph=world_highways_and_marnet_graph,
        origin_id=0,
        destination_id=5
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
        graph=world_highways_and_marnet_graph,
        node_id=0
    ),
)
