# SCGraph Utils
from scgraph.spanning import SpanningTree as SCSpanning
# Other Utilities
from pamda import pamda
from pamda.pamda_timer import pamda_timer

# Local Imports and Utils
from bmsspy.solvers import bmssp
from utils.graphs import make_nxgraph, make_igraph, make_gridgraph, get_nx_shortest_path, get_igraph_shortest_path


graph_data = [
    ('100x100 GridGraph', make_gridgraph(100, 100)),
    ('200x200 GridGraph', make_gridgraph(200, 200)),
    ('400x400 GridGraph', make_gridgraph(400, 400)),
    ('800x800 GridGraph', make_gridgraph(800, 800)),
    ('1600x1600 GridGraph', make_gridgraph(1600, 1600)),
    ('3200x3200 GridGraph', make_gridgraph(3200, 3200)),
]

output = []

print("\n===============\nIGraph vs NetworkX vs SCGraph vs BMSSPy Time Tests:\n===============")
for name, scgraph_object in graph_data:
    print(f"\n{name}:")
    scgraph = scgraph_object.graph
    # nxgraph = make_nxgraph(scgraph)
    # igraph = make_igraph(scgraph)

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
    # graph_edges = nxgraph.number_of_edges()


    for case_name, origin in test_cases:
        print(f"\nTesting {case_name}...")

        bmssp_spantree_time_stats = pamda_timer(bmssp, iterations = 10).get_time_stats(graph=scgraph, origin_id=origin)
        print(f"BMSSP time: {bmssp_spantree_time_stats['avg']:.2f} ms (stdev: {bmssp_spantree_time_stats['std']:.2f})")

        sc_dijkstra_spantree_time_stats = pamda_timer(SCSpanning.makowskis_spanning_tree, iterations = 10).get_time_stats(graph=scgraph, node_id=origin)
        print(f"SCGraph Dijkstra Modified spantree Tree time: {sc_dijkstra_spantree_time_stats['avg']:.2f} ms (stdev: {sc_dijkstra_spantree_time_stats['std']:.2f})")

        # nx_dijkstra_spantree_time_stats = pamda_timer(get_nx_shortest_path, iterations = 10).get_time_stats(graph=nxgraph, origin=origin)
        # print(f"NetworkX Dijkstra time: {nx_dijkstra_spantree_time_stats['avg']:.2f} ms (stdev: {nx_dijkstra_spantree_time_stats['std']:.2f})")

        # try:
        #     ig_spantree_time_stats = pamda_timer(get_igraph_shortest_path, iterations = 10).get_time_stats(graph=igraph, origin=origin)
        #     print(f"iGraph spantree time: {ig_spantree_time_stats['avg']:.2f} ms (stdev: {ig_spantree_time_stats['std']:.2f})")
        # except Exception as e:
        #     ig_spantree_time_stats = {'avg': float('nan'), 'std': float('nan')}
        #     print(f"iGraph spantree time: {ig_spantree_time_stats['avg']:.2f} ms (stdev: {ig_spantree_time_stats['std']:.2f})")

        output.append({
            'graph_name': name,
            'case_name': case_name,
            'graph_nodes': graph_nodes,
            # 'graph_edges': graph_edges,
            # Times in milliseconds
            'bmssp_spantree_time_ms': bmssp_spantree_time_stats['avg'],
            'sc_dijkstra_spantree_time_ms': sc_dijkstra_spantree_time_stats['avg'],
            # 'nx_dijkstra_spantree_time_ms': nx_dijkstra_spantree_time_stats['avg'],
            # 'ig_spantree_time_ms': ig_spantree_time_stats['avg'],
            # Standard Deviations in milliseconds
            'bmssp_spantree_stdev': bmssp_spantree_time_stats['std'],
            'sc_dijkstra_spantree_stdev': sc_dijkstra_spantree_time_stats['std'],
            # 'nx_dijkstra_spantree_stdev': nx_dijkstra_spantree_time_stats['std'],
            # 'ig_spantree_stdev': ig_spantree_time_stats['std'],
        })

pamda.write_csv(
    filename="benchmarking/outputs/gridscale_time_tests.csv",
    data=output
)