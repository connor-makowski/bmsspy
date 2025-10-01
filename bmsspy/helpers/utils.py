inf = float("inf")


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
