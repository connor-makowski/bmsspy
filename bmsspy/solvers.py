from .bmssp_solver import BmsspSolver
from .utils import input_check, reconstruct_path


def bmssp(
    graph: list[dict[int, int | float]],
    origin_id: int,
    destination_id: int = None,
):
    """
    Function:

    - A Full BMSSP-style shortest path solver.
    - Return a dictionary of various path information including:
        - `id_path`: A list of node ids in the order they are visited
        - `path`: A list of node dictionaries (lat + long) in the order they are visited

    Required Arguments:

    - `graph`:
        - Type: list of dictionaries
    - `origin_id`
        - Type: int
        - What: The id of the origin node from the graph dictionary to start the shortest path from
    - `destination_id`
        - Type: int | None
        - What: The id of the destination node from the graph dictionary to end the shortest path at
        - Note: If None, returns the distance matrix and predecessor list for the origin node
        - Note: If provided, returns the shortest path [origin_id, ..., destination_id] and its length

    Optional Arguments:

    - None
    """
    # Input Validation
    input_check(graph=graph, origin_id=origin_id, destination_id=destination_id)
    # Run the BMSSP Algorithm to relax as many edges as possible.
    solver = BmsspSolver(graph, origin_id)
    if destination_id is not None:
        if solver.distance_matrix[destination_id] == float("inf"):
            raise Exception(
                "Something went wrong, the origin and destination nodes are not connected."
            )

    return {
        "origin_id": origin_id,
        "destination_id": destination_id,
        "predecessor": solver.predecessor,
        "distance_matrix": solver.distance_matrix,
        "path": (
            reconstruct_path(
                destination_id=destination_id, predecessor=solver.predecessor
            )
            if destination_id
            else None
        ),
        "length": (
            solver.distance_matrix[destination_id] if destination_id else None
        ),
    }