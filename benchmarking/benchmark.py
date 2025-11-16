# Small Geographs
from scgraph.geographs.marnet import marnet_geograph
from scgraph.geographs.north_america_rail import north_america_rail_geograph
from scgraph.geographs.oak_ridge_maritime import oak_ridge_maritime_geograph
from scgraph.geographs.us_freeway import us_freeway_geograph

# Large Geographs
from scgraph_data.world_highways_and_marnet import world_highways_and_marnet_geograph
# from scgraph_data.world_highways import world_highways_geograph
# from scgraph_data.world_railways import world_railways_geograph

# Utilities
from pamda import pamda

# Local Imports and Utils
from utils.graphs import make_nxgraph, make_igraph, make_gridgraph
from utils.time_case import time_case


graph_data = [
    # Geographs
    # Small Geographs
    ('Geograph Marnet', marnet_geograph),
    ('Geograph North America Rail', north_america_rail_geograph),
    ('Geograph Oak Ridge Maritime', oak_ridge_maritime_geograph),
    ('Geograph US Freeway', us_freeway_geograph),
    # Large Geographs
    ('Geograph World Highways and Marnet', world_highways_and_marnet_geograph),
    # ('Geograph World Highways', world_highways_geograph), # Ignore for testing since it is fairly disconnected
    # ('Geograph World Railways', world_railways_geograph), # Ignore for testing since it is fairly disconnected

    # GridGraphs
    # Square GridGraphs
    ('square_gridgraph_15x15', make_gridgraph(15, 15)),
    ('square_gridgraph_25x25', make_gridgraph(25, 25)),
    ('Square GridGraph 50x50', make_gridgraph(50, 50)),
    ('Square GridGraph 75x75', make_gridgraph(75, 75)),
    ('Square GridGraph 100x100', make_gridgraph(100, 100)),
    ('Square GridGraph 250x250', make_gridgraph(250, 250)),
    ('Square GridGraph 500x500', make_gridgraph(500, 500)),
    ('Square GridGraph 1000x1000', make_gridgraph(1000, 1000)),
    # Rectangular GridGraphs
    ('Rectangular_gridgraph_15x50', make_gridgraph(15, 50)),
    ('Rectangular_gridgraph_25x50', make_gridgraph(25, 50)),
    ('Rectangular GridGraph 25x100', make_gridgraph(25, 100)),
    ('Rectangular GridGraph 50x100', make_gridgraph(50, 100)),
    ('Rectangular GridGraph 50x200', make_gridgraph(50, 200)),
    ('Rectangular GridGraph 100x500', make_gridgraph(100, 500)),
    ('Rectangular GridGraph 100x1000', make_gridgraph(100, 1000)),
    ('Rectangular GridGraph 100x1500', make_gridgraph(100, 1500)),
    ('Rectangular GridGraph 100x2000', make_gridgraph(100, 2000)),
]

output = []

print("\n===============\nGeneral Time Tests:\n===============")
for name, scgraph_object in graph_data:
    print(f"\n{name}:")
    scgraph = scgraph_object.graph
    nxgraph = make_nxgraph(scgraph)
    igraph = make_igraph(scgraph)

    # Warmup the GeoKDTree
    try:
        scgraph_object.warmup()
    except:
        pass

    if 'gridgraph' in name.lower():
        test_cases = [
            ('bottom_left', scgraph_object.get_idx(**{"x": 5, "y": 5})),
            ('top_right', scgraph_object.get_idx(**{"x": scgraph_object.x_size-5, "y": scgraph_object.y_size-5})),
            ('center',scgraph_object.get_idx(**{"x": int(scgraph_object.x_size/2)-5, "y": int(scgraph_object.y_size/2)})),
        ]
    else:
        test_cases = [
            ('los_angeles', scgraph_object.geokdtree.closest_idx([34.0522, -118.2437])), # Los Angeles
            ('new_york', scgraph_object.geokdtree.closest_idx([40.7128, -74.0060])), # New York
            ('seattle', scgraph_object.geokdtree.closest_idx([47.6062, -122.3321])), # Seattle
        ]

    graph_nodes = len(scgraph)
    graph_edges = nxgraph.number_of_edges()

    for case_name, origin in test_cases:
        output.append(time_case(
            graph_name = name,
            case_name = case_name,
            origin = origin,
            scgraph = scgraph,
            nxgraph = nxgraph,
            igraph = igraph,
            test_vanilla_dijkstra = True,
            print_console = True,
            iterations = 25,
        ))

import platform
if platform.python_implementation() == 'PyPy':
    print("Code is running under PyPy.")
    pamda.write_csv(
        filename="benchmarking/outputs/pypy_benchmark_time_tests.csv",
        data=output
    )
else:
    print(f"Code is running under {platform.python_implementation()}.")
    pamda.write_csv(
        filename="benchmarking/outputs/benchmark_time_tests.csv",
        data=output
    )