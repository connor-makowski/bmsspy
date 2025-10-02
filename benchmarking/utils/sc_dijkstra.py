
from .heapq import heappop, heappush
from bmsspy.helpers.heapdict import heapdict

def pure_python_sc_dijkstra(graph: list[dict], node_id: int) -> dict:
    """
    Modified version of Makowski's spaning tree algorithm forcing use of heapq in pure python (not using C if available).

    """
    # Input Validation
    assert isinstance(node_id, int), "node_id must be an integer"
    assert 0 <= node_id < len(graph), "node_id must be a valid node id"
    # Variable Initialization
    distance_matrix = [float("inf")] * len(graph)
    distance_matrix[node_id] = 0
    open_leaves = []
    heappush(open_leaves, (0, node_id))
    predecessor = [-1] * len(graph)

    while open_leaves:
        current_distance, current_id = heappop(open_leaves)
        for connected_id, connected_distance in graph[current_id].items():
            possible_distance = current_distance + connected_distance
            if possible_distance < distance_matrix[connected_id]:
                distance_matrix[connected_id] = possible_distance
                predecessor[connected_id] = current_id
                heappush(open_leaves, (possible_distance, connected_id))

    return {
        "node_id": node_id,
        "predecessors": predecessor,
        "distance_matrix": distance_matrix,
    }

def pure_python_heapdict_sc_dijkstra(graph: list[dict], node_id: int) -> dict:
    """
    Modified version of Makowski's spaning tree algorithm forcing use of a heapdict in pure python (not using C if available).

    Uses a heapdict for potentially better performance on large graphs.
    """
    # Input Validation
    assert isinstance(node_id, int), "node_id must be an integer"
    assert 0 <= node_id < len(graph), "node_id must be a valid node id"
    # Variable Initialization
    distance_matrix = [float("inf")] * len(graph)
    distance_matrix[node_id] = 0
    open_leaves = heapdict()
    open_leaves[node_id] = 0
    predecessor = [-1] * len(graph)

    while open_leaves.heap:
        current_id, current_distance = open_leaves.popitem()
        for connected_id, connected_distance in graph[current_id].items():
            possible_distance = current_distance + connected_distance
            if possible_distance < distance_matrix[connected_id]:
                distance_matrix[connected_id] = possible_distance
                predecessor[connected_id] = current_id
                open_leaves[connected_id] = possible_distance

    return {
        "node_id": node_id,
        "predecessors": predecessor,
        "distance_matrix": distance_matrix,
    }