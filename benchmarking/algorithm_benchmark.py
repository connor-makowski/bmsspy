# Small Geographs
from scgraph.geographs.marnet import marnet_geograph
from scgraph.geographs.north_america_rail import north_america_rail_geograph
from scgraph.geographs.oak_ridge_maritime import oak_ridge_maritime_geograph
from scgraph.geographs.us_freeway import us_freeway_geograph
# Large Geographs
from scgraph_data.world_highways_and_marnet import world_highways_and_marnet_geograph
from scgraph_data.world_highways import world_highways_geograph
from scgraph_data.world_railways import world_railways_geograph

# Utilities
from pamda import pamda

# Local Imports and Utils
from utils.graphs import make_nxgraph, make_igraph, make_gridgraph
from utils.time_case import time_case


graph_data = [
    # Small Geographs
    ('Marnet', marnet_geograph),
    ('North America Rail', north_america_rail_geograph),
    ('Oak Ridge Maritime', oak_ridge_maritime_geograph),
    ('US Freeway', us_freeway_geograph),
    # Large Geographs
    ('World Highways and Marnet', world_highways_and_marnet_geograph),
    ('World Highways', world_highways_geograph),
    ('World Railways', world_railways_geograph),
    # Square GridGraphs
    ('100x100 GridGraph', make_gridgraph(100, 100)),
    ('200x200 GridGraph', make_gridgraph(200, 200)),
    ('300x300 GridGraph', make_gridgraph(300, 300)),
    ('400x400 GridGraph', make_gridgraph(400, 400)),
    # Rectangular GridGraphs
    ('100x500 GridGraph', make_gridgraph(100, 500)),
    ('500x100 GridGraph', make_gridgraph(500, 100)),
]

output = []

print("\n===============\nGeneral Time Tests:\n===============")
for name, scgraph_object in graph_data:
    print(f"\n{name}:")
    scgraph = scgraph_object.graph
    nxgraph = make_nxgraph(scgraph)
    igraph = make_igraph(scgraph)

    if 'gridgraph' in name.lower():
        test_cases = [
            ('bottomLeft', scgraph_object.get_idx(**{"x": 5, "y": 5})),
            ('topRight', scgraph_object.get_idx(**{"x": scgraph_object.x_size-5, "y": scgraph_object.y_size-5})),
            ('center',scgraph_object.get_idx(**{"x": int(scgraph_object.x_size/2)-5, "y": int(scgraph_object.y_size/2)})),
        ]
    else:
        test_cases = [
            ('case_1', 0),
            ('case_2', 100),
            ('case_3', 1000),
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
            print_console = True
        ))

pamda.write_csv(
    filename="benchmarking/outputs/algorithm_time_tests.csv",
    data=output
)