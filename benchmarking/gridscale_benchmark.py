# Utilities
from pamda import pamda

# Local Imports and Utils
from utils.graphs import make_gridgraph
from utils.time_case import time_case


graph_data = [
    ('25x25 GridGraph', make_gridgraph(25, 25)),
    ('50x50 GridGraph', make_gridgraph(50, 50)),
    ('100x100 GridGraph', make_gridgraph(100, 100)),
    ('200x200 GridGraph', make_gridgraph(200, 200)),
    ('400x400 GridGraph', make_gridgraph(400, 400)),
    ('800x800 GridGraph', make_gridgraph(800, 800)),
    ('1600x1600 GridGraph', make_gridgraph(1600, 1600)),
    ('3200x3200 GridGraph', make_gridgraph(3200, 3200)),
]

output = []

print("\n===============\nGridGraph Time Tests:\n===============")
for name, scgraph_object in graph_data:
    print(f"\n{name}:")
    scgraph = scgraph_object.graph

    test_cases = [
        ('bottom_left', scgraph_object.get_idx(**{"x": 5, "y": 5})),
        ('top_right', scgraph_object.get_idx(**{"x": scgraph_object.x_size-5, "y": scgraph_object.y_size-5})),
        ('center',scgraph_object.get_idx(**{"x": int(scgraph_object.x_size/2)-5, "y": int(scgraph_object.y_size/2)})),
    ]

    graph_nodes = len(scgraph)

    for case_name, origin in test_cases:
        output.append(time_case(
            graph_name = name,
            case_name = case_name,
            origin = origin,
            scgraph = scgraph,
            print_console = True,
            iterations = 10
        ))

import platform
if platform.python_implementation() == 'PyPy':
    print("Code is running under PyPy.")
    pamda.write_csv(
        filename="benchmarking/outputs/pypy_gridscale_time_tests.csv",
        data=output
    )
else:
    print(f"Code is running under {platform.python_implementation()}.")
    pamda.write_csv(
        filename="benchmarking/outputs/gridscale_time_tests.csv",
        data=output
    )