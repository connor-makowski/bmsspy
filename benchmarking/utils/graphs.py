
from scgraph.grid import GridGraph
from networkx import Graph as NXGraph, multi_source_dijkstra
from igraph import Graph as IGGraph

def make_nxgraph(graph):
    """
    Convert a scgraph graph object to a NetworkX graph.
    """
    nxGraph = NXGraph()
    for idx_from, connections in enumerate(graph):
        for idx_to, weight in connections.items():
            nxGraph.add_edge(idx_from, idx_to, weight=weight)
    return nxGraph

def make_igraph(graph):
    """
    Convert a scgraph graph object to an igraph graph.
    """
    edges = []
    weights = []

    for from_node, neighbors in enumerate(graph):
        for to_node, weight in neighbors.items():
            # iGraph assumes undirected graph by default, avoid adding reverse edge
            if from_node < to_node:
                edges.append((from_node, to_node))
                weights.append(weight)

    ig_graph = IGGraph(edges=edges, directed=False)
    ig_graph.es['weight'] = weights
    return ig_graph


def make_gridgraph(x_size, y_size):
    # Create a wall down the middle of the grid
    blocks = [(int(x_size/2), i) for i in range(5, y_size)]
    shape = [(0, 0), (0, 1), (1, 0), (1, 1)]
    return GridGraph(
        x_size=x_size,
        y_size=y_size,
        blocks=blocks,
        shape=shape,
        add_exterior_walls=False,
)

def get_igraph_shortest_path(graph, origin):
    """
    Get the shortest path in an igraph graph.
    """
    distance_matrix = graph.get_shortest_paths(origin, weights='weight')[0]
    return {
        'distance_matrix': distance_matrix,
    }

def get_nx_shortest_path(graph, origin):
    return multi_source_dijkstra(G=graph, sources={origin}, weight='weight')