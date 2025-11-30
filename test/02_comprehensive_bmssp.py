# General Imports
import time
from pamda import pamda
from scgraph.utils import hard_round
from scgraph.spanning import SpanningTree

# Geographs
from scgraph.geographs.marnet import graph as marnet_graph
from scgraph.geographs.us_freeway import graph as us_freeway_graph
from scgraph_data.world_highways_and_marnet import (
    graph as world_highways_and_marnet_graph,
)

# Local Imports
from bmsspy import Bmssp
from bmsspy.data_structures.heap_data_structure import BmsspHeapDataStructure
from bmsspy.data_structures.unique_data_structure import UniqueBmsspDataStructure


print("\n===============\nBMSSP VS SCGraph Tests:\n===============")


def validate(name, realized, expected):
    # Custom lenth rounding for floating point precision issues
    realized = [
        (
            hard_round(6, float(val))
            if float(val) != float("inf")
            else float("inf")
        )
        for val in realized
    ]
    expected = [
        (
            hard_round(6, float(val))
            if float(val) != float("inf")
            else float("inf")
        )
        for val in expected
    ]
    if realized == expected:
        print(f"{name}: PASS")
    else:
        print(f"{name}: FAIL")
        # for idx in range(len(realized)):
        #     if realized[idx] != expected[idx]:
        #         print(
        #             f"  Node {idx}: Realized={realized[idx]}, Expected={expected[idx]}"
        #         )
        #         raise Exception("Test Failed")
        # print("Expected:", expected)
        # print("Realized:", realized)


def check_correctness(name, graph, origin_id):
    # Since the BMSSP conversion function can not take 0 lenghts, we test it vs
    # the constant degree converted graph trimmed to the original graph size
    bmssp_graph = Bmssp(graph=graph)
    dm_sp_tree = SpanningTree.makowskis_spanning_tree(graph, origin_id)
    validate(
        name=name + " (Standard)",
        realized=bmssp_graph.solve(origin_id=origin_id)["distance_matrix"],
        expected=dm_sp_tree[
            "distance_matrix"
        ],  # Trimmed to original graph size
    )
    bmssp_heap_function = bmssp_graph.solve(
        origin_id=origin_id, data_structure=BmsspHeapDataStructure
    )
    validate(
        name=name + " (Heap)",
        realized=bmssp_heap_function["distance_matrix"],
        expected=dm_sp_tree[
            "distance_matrix"
        ],  # Trimmed to original graph size
    )

    bmssp_no_cd = Bmssp(graph=graph, use_constant_degree_graph=False)
    dm_sp_tree_no_cd = SpanningTree.makowskis_spanning_tree(graph, origin_id)
    validate(
        name=name + "(Not Constant Degree)",
        realized=bmssp_no_cd.solve(origin_id=origin_id)["distance_matrix"],
        expected=dm_sp_tree_no_cd[
            "distance_matrix"
        ],  # Trimmed to original graph size
    )

    validate(
        name=name + "(Not Constant Degree HashMap)",
        realized=bmssp_no_cd.solve(
            origin_id=origin_id, data_structure=UniqueBmsspDataStructure
        )["distance_matrix"],
        expected=dm_sp_tree_no_cd[
            "distance_matrix"
        ],  # Trimmed to original graph size
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

print("\n===============\nBMSSP Time Tests:\n===============")

marnet_graph_bmssp = Bmssp(graph=marnet_graph)
us_freeway_graph_bmssp = Bmssp(graph=us_freeway_graph)
world_highways_and_marnet_graph_bmssp = Bmssp(
    graph=world_highways_and_marnet_graph
)

marnet_graph_bmssp_no_cd = Bmssp(
    graph=marnet_graph, use_constant_degree_graph=False
)
us_freeway_graph_bmssp_no_cd = Bmssp(
    graph=us_freeway_graph, use_constant_degree_graph=False
)
world_highways_and_marnet_graph_bmssp_no_cd = Bmssp(
    graph=world_highways_and_marnet_graph, use_constant_degree_graph=False
)

time_test(
    "BMSSP 1 (marnet)",
    pamda.thunkify(marnet_graph_bmssp.solve)(origin_id=0, destination_id=5),
)
time_test(
    "BMSSP 2 (marnet)",
    pamda.thunkify(marnet_graph_bmssp.solve)(
        origin_id=100, destination_id=7999
    ),
)
time_test(
    "BMSSP 3 (marnet)",
    pamda.thunkify(marnet_graph_bmssp.solve)(
        origin_id=4022, destination_id=8342
    ),
)

time_test(
    "BMSSP 4 (us_freeway)",
    pamda.thunkify(us_freeway_graph_bmssp.solve)(origin_id=0, destination_id=5),
)

time_test(
    "BMSSP 5 (us_freeway)",
    pamda.thunkify(us_freeway_graph_bmssp.solve)(
        origin_id=4022, destination_id=8342
    ),
)

time_test(
    "BMSSP 6 (world_highways_and_marnet)",
    pamda.thunkify(world_highways_and_marnet_graph_bmssp.solve)(
        origin_id=0, destination_id=5
    ),
)

time_test(
    "BMSSP 7 (heap) (world_highways_and_marnet)",
    pamda.thunkify(world_highways_and_marnet_graph_bmssp.solve)(
        origin_id=0, destination_id=5, data_structure=BmsspHeapDataStructure
    ),
)

time_test(
    "BMSSP 8 (not constant degree) (world_highways_and_marnet)",
    pamda.thunkify(world_highways_and_marnet_graph_bmssp_no_cd.solve)(
        origin_id=0, destination_id=5
    ),
)

time_test(
    "BMSSP 8 (not constant degree HashMap) (world_highways_and_marnet)",
    pamda.thunkify(world_highways_and_marnet_graph_bmssp_no_cd.solve)(
        origin_id=0, destination_id=5, data_structure=UniqueBmsspDataStructure
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
