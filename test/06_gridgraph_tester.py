from scgraph import GridGraph
from scgraph.utils import hard_round
from bmsspy.solvers import Bmssp
from scgraph.spanning import SpanningTree
from bmsspy.helpers.utils import convert_to_constant_degree
from bmsspy.data_structures.heap_data_structure import BmsspDataStructure

print("\n===============\nBMSSP GridGraph Tests:\n===============")


def make_gridgraph(x_size, y_size):
    # Create a wall down the middle of the grid
    blocks = [(int(x_size / 2), i) for i in range(5, y_size)]
    shape = [(0, 0), (0, 1), (1, 0), (1, 1)]
    return GridGraph(
        x_size=x_size,
        y_size=y_size,
        blocks=blocks,
        shape=shape,
        add_exterior_walls=False,
    )

def validate(name, realized, expected):
    # Custom lenth rounding for floating point precision issues
    realized = [hard_round(4, val) if val!=float('inf') else float('inf') for val in realized]
    expected = [hard_round(4, val) if val!=float('inf') else float('inf') for val in expected]
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
    bmssp_graph_output = bmssp_graph.solve(origin_id=origin_id)
    dm_sp_tree = SpanningTree.makowskis_spanning_tree(
        graph, origin_id
    )
    validate(
        name=name + " (Standard)",
        realized=bmssp_graph_output["distance_matrix"],
        expected=dm_sp_tree["distance_matrix"][:len(graph)],  # Trimmed to original graph size
    )
    bmssp_heap_output = bmssp_graph.solve(
        origin_id=origin_id, data_structure=BmsspDataStructure
    )
    validate(
        name=name + " (Heap)",
        realized=bmssp_heap_output["distance_matrix"],
        expected=dm_sp_tree["distance_matrix"][:len(graph)],  # Trimmed to original graph size
    )


for gridgraph_size in [25, 50, 100]:
    gridgraph = make_gridgraph(gridgraph_size, gridgraph_size)
    test_cases = [
        ("bottom_left", {"x": 5, "y": 5}),
        ("top_right", {"x": gridgraph.x_size - 5, "y": gridgraph.y_size - 5}),
        (
            "center",
            {
                "x": int(gridgraph.x_size / 2) - 5,
                "y": int(gridgraph.y_size / 2),
            },
        ),
    ]
    for case_name, origin_dict in test_cases:
        origin_idx = gridgraph.get_idx(**origin_dict)

        check_correctness(
            name=f"BMSSP Gridgraph {gridgraph_size}x{gridgraph_size} {case_name}",
            graph=gridgraph.graph,
            origin_id=origin_idx,
        )
