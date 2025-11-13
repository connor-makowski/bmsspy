from copy import deepcopy
from decimal import Decimal

inf = Decimal("Infinity")


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


def convert_to_constant_degree(graph: list[dict[int, int | float]]) -> dict:
    """
    Convert a graph to a guaranteed unique path length based constant degree graph with no more than 2 incoming and 2 outgoing edges per node.

    The precision value determines the number of decimal places to maintain when adjusting edge weights to ensure unique path lengths.

    Args:

    - graph (list of dict): The input graph represented as an adjacency list.

    Returns:

    - dict: A dictionary containing the converted constant degree graph and the output mapping.
        - 'graph' (list of dict): The converted constant degree graph.
        - 'idx_map' (list of int): A mapping from all node indices to original node indices.
            - Eg: idx_map[5] = 2 means node 5 in the new graph corresponds to node 2 in the original graph.
            - Note: All nodes below the original graph length map to themselves.
        - 'original_graph_len' (int): The length of the original graph.
    """
    # Determine if the graph needs to be converted to constant degree
    #   - (two in / two out)
    #   - Or
    #   - One of (one in / two out) (two in / one out)
    two_in_two_out = True
    original_graph_len = len(graph)
    graph = deepcopy(graph)
    in_graph = [{} for _ in range(len(graph))]
    for node_idx, node_neighbors in enumerate(graph):
        for neighbor, weight in node_neighbors.items():
            weight = Decimal(weight)
            graph[node_idx][neighbor] = weight
            in_graph[neighbor][node_idx] = weight

    nodes_to_partition = {}
    for node_idx in range(len(graph)):
        indegree = len(in_graph[node_idx])
        outdegree = len(graph[node_idx])
        if indegree > 2 or outdegree > 2 or (indegree + outdegree) > 3:
            if two_in_two_out:
                nodes_to_partition[node_idx] = max(indegree, outdegree)
            else:
                nodes_to_partition[node_idx] = indegree + outdegree

    idx_map = list(range(len(graph)))

    for node_idx, num_partitions in nodes_to_partition.items():
        local_idx_mapping = [node_idx] + list(
            range(len(graph), len(graph) + num_partitions - 1)
        )
        graph.extend([{} for _ in range(num_partitions - 1)])
        in_graph.extend([{} for _ in range(num_partitions - 1)])
        idx_map.extend([node_idx] * (num_partitions - 1))

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

        if two_in_two_out:
            local_idx = 0
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
            graph[from_idx][to_idx] = Decimal(0)
            in_graph[to_idx][from_idx] = Decimal(0)

    return {
        "graph": graph,
        "idx_map": idx_map,
        "original_graph_len": original_graph_len,
    }


def convert_from_constant_degree(
    distance_matrix, predecessor_matrix, constant_degree_dict
):
    """
    Convert the distance and predecessor matrices from a constant degree graph back to the equivalent matrices for the original graph.

    Args:

    - distance_matrix (list of float): The distance matrix from the constant degree graph.
    - predecessor_matrix (list of int): The predecessor matrix from the constant degree graph.
    - constant_degree_dict (dict): The dictionary returned by `convert_to_constant_degree` function.

    Returns:

    - dict: A dictionary containing the converted distance and predecessor matrices.
        - 'distance_matrix' (list of float): The converted distance matrix for the original graph.
        - 'predecessor_matrix' (list of int): The converted predecessor matrix for the original graph.
    """
    cd_idx_map = constant_degree_dict["idx_map"]
    cd_original_graph_len = constant_degree_dict["original_graph_len"]

    predecessor_matrix_converted = []
    for loc_idx, node_idx in enumerate(
        predecessor_matrix[:cd_original_graph_len]
    ):
        while True:
            if node_idx == -1:
                predecessor_matrix_converted.append(node_idx)
                break
            else:
                mapped_node_idx = cd_idx_map[node_idx]
                if (
                    mapped_node_idx < cd_original_graph_len
                    and mapped_node_idx != loc_idx
                ):
                    predecessor_matrix_converted.append(mapped_node_idx)
                    break
                else:
                    node_idx = predecessor_matrix[node_idx]

    return {
        "distance_matrix": distance_matrix[:cd_original_graph_len],
        "predecessor_matrix": predecessor_matrix_converted,
    }
