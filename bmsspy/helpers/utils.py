inf = float("inf")
from copy import deepcopy


def input_check(
    graph: list[dict[int, int | float]], origin_id: int, destination_id: int
) -> None:
    """
    Function:

    - Check that the inputs passed to the shortest path algorithm are valid
    - Raises an exception if the inputs passed are not valid

    Required Arguments:

    - `graph`:
        - Type: list of dictionaries
    - `origin_id`
        - Type: int
        - What: The id of the origin node from the graph dictionary to start the shortest path from
    - `destination_id`
        - Type: int
        - What: The id of the destination node from the graph dictionary to end the shortest path at

    Optional Arguments:

    - None
    """
    if (
        not isinstance(origin_id, int)
        and origin_id < len(graph)
        and origin_id >= 0
    ):
        raise Exception(f"Origin node ({origin_id}) is not in the graph")
    if destination_id is None:
        pass
    elif (
        not isinstance(destination_id, int)
        and origin_id < len(graph)
        and origin_id >= 0
    ):
        raise Exception(
            f"Destination node ({destination_id}) is not in the graph"
        )


def reconstruct_path(destination_id: int, predecessor: list[int]) -> list[int]:
    """
    Function:

    - Reconstruct the shortest path from the destination node to the origin node
    - Return the reconstructed path in the correct order
    - Given the predecessor list, this function reconstructs the path

    Required Arguments:

    - `destination_id`
        - Type: int
        - What: The id of the destination node from the graph dictionary to end the shortest path at
    - `predecessor`
        - Type: list[int]
        - What: The predecessor list that was used to compute the shortest path
        - This list is used to reconstruct the path from the destination node to the origin node
        - Note: Nodes with no predecessor should be -1

    Optional Arguments:

    - None
    """
    output_path = [destination_id]
    while predecessor[destination_id] != -1:
        destination_id = predecessor[destination_id]
        output_path.append(destination_id)
    output_path.reverse()
    return output_path


def convert_to_constant_degree(graph):
    """
    Convert a graph to a constant degree graph with no more than 2 incoming and 2 outgoing edges per node.
    
    Parameters:
    graph (list of dict): The input graph represented as an adjacency list.
    
    Returns:
    dict: A dictionary containing the converted constant degree graph and the output mapping.
        - 'graph' (list of dict): The converted constant degree graph.
        - 'idx_map' (dict): A mapping from all node indices to original node indices.
            - Keys are node indices in the converted graph.
            - Values are the corresponding original node indices.
            - Note: All nodes below the original graph length map to themselves.
    """
    graph = deepcopy(graph)
    in_graph = [{} for _ in range(len(graph))]
    for node_idx, node_neighbors in enumerate(graph):
        for neighbor, weight in node_neighbors.items():
            in_graph[neighbor][node_idx] = weight
    
    nodes_to_partition = {}
    for node_idx in range(len(graph)):
        indegree = len(in_graph[node_idx])
        outdegree = len(graph[node_idx])
        if indegree > 2 or outdegree > 2 or (indegree + outdegree) > 3:
            nodes_to_partition[node_idx] = indegree + outdegree

    idx_map = {idx: idx for idx in range(len(graph))}

    for node_idx, num_partitions in nodes_to_partition.items():
        local_idx_mapping = [node_idx] + list(range(len(graph), len(graph) + num_partitions - 1))
        graph.extend([{} for _ in range(num_partitions - 1)])
        in_graph.extend([{} for _ in range(num_partitions - 1)])
        for local_idx in local_idx_mapping:
            idx_map[local_idx] = node_idx

        out_dict = dict(graph[node_idx])
        in_dict = dict(in_graph[node_idx])

        graph[node_idx] = {}
        in_graph[node_idx] = {}

        local_idx = 0

        # Break the node into partitions assigning one outgoing edge per node
        for out_node_idx, out_node_weight in out_dict.items():
            new_idx = local_idx_mapping[local_idx]
            graph[new_idx][out_node_idx] = out_node_weight
            in_graph[out_node_idx].pop(node_idx, None)
            in_graph[out_node_idx][new_idx] = out_node_weight
            local_idx += 1

        # Break the node into partitions assigning one incoming edge per node
        for in_node_idx, in_node_weight in in_dict.items():
            new_idx = local_idx_mapping[local_idx]
            in_graph[new_idx][in_node_idx] = in_node_weight
            graph[in_node_idx].pop(node_idx, None)
            graph[in_node_idx][new_idx] = in_node_weight
            local_idx += 1

        # Cycle connect all partitions with zero-weight edges
        for item_idx in range(len(local_idx_mapping)):
            from_idx = local_idx_mapping[item_idx]
            to_idx = local_idx_mapping[(item_idx + 1) % len(local_idx_mapping)]
            graph[from_idx][to_idx] = 1e-8
            in_graph[to_idx][from_idx] = 1e-8

    return {
        "graph": graph,
        "idx_map": idx_map
    }