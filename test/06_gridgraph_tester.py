from scgraph import GridGraph
from bmsspy.solvers import bmssp
from scgraph.spanning import SpanningTree
from bmsspy.helpers.utils import convert_to_constant_degree

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

        graph = convert_to_constant_degree(gridgraph.graph)["graph"]
        scspan_output = SpanningTree.makowskis_spanning_tree(
            graph, origin_idx
        )
        bmssp_output = bmssp(gridgraph.graph, origin_idx)

        output_text = f"Gridgraph ({case_name}, {origin_dict}) on {gridgraph.x_size}x{gridgraph.y_size} matrix: "
        if bmssp_output["distance_matrix"] == scspan_output["distance_matrix"]:
            print(f"{output_text}PASS")
        else:
            success = True
            for idx in range(len(gridgraph.graph)):
                if (
                    abs(bmssp_output['distance_matrix'][idx] - scspan_output['distance_matrix'][idx]) > 1e-6
                ):
                    print(f"{output_text}FAIL")
                    # print(
                    #     f"  Node {idx}: BMSSP={bmssp_output['distance_matrix'][idx]}, SCSpan={scspan_output['distance_matrix'][idx]}"
                    # )
                    success=False
                    break
            if success:
                print(f"{output_text}PASS")
