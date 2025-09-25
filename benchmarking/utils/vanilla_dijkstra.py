def vanilla_dijkstra(
    graph: list[dict[int, int | float]], origin_id: int
) -> dict:
    """
    Function:

    - Identify the distance and predecessor for each node in the graph from the origin node using Dijkstra's algorithm
    - This is a vanilla implementation of Dijkstra's algorithm without any optimizations
    - This implementation does not use a priority queue, so it is less efficient than optimized versions
    - Return a dictionary of various path information including:
        - `distance_matrix`: A list of the shortest distance from the origin node to each node in the graph
        - `predecessor`: A list of the predecessor node for each node in the graph

    Required Arguments:

    - `graph`:
        - Type: list of dictionaries
        - See: https://connor-makowski.github.io/scgraph/scgraph/graph.html#Graph.validate_graph
    - `origin_id`
        - Type: int
        - What: The id of the origin node from the graph dictionary to start the shortest path from

    Optional Arguments:

    - None
    """
    distance_matrix = [float("inf")] * len(graph)
    branch_tip_distances = [float("inf")] * len(graph)
    predecessor = [-1] * len(graph)

    distance_matrix[origin_id] = 0
    branch_tip_distances[origin_id] = 0

    while True:
        current_distance = min(branch_tip_distances)
        if current_distance == float("inf"):
            break
        current_id = branch_tip_distances.index(current_distance)
        branch_tip_distances[current_id] = float("inf")
        for connected_id, connected_distance in graph[current_id].items():
            possible_distance = current_distance + connected_distance
            if possible_distance < distance_matrix[connected_id]:
                distance_matrix[connected_id] = possible_distance
                predecessor[connected_id] = current_id
                branch_tip_distances[connected_id] = possible_distance

    return {
        "distance_matrix": distance_matrix,
        "predecessor": predecessor,
    }