from .core import BmsspCore
from .helpers.utils import input_check, reconstruct_path, convert_to_constant_degree, convert_from_constant_degree

from bmsspy.data_structures.data_structure import BmsspDataStructure

class Bmssp:
    def __init__(self, graph: list[dict[int, int | float]]):
        """
        Function:

        - Initialize a BMSSP-style shortest path object and calculate the constant degree graph and related info.

        Required Arguments:

        - `graph`:
            - Type: list of dictionaries
        """
        self.graph = graph
        self.constant_degree_dict = convert_to_constant_degree(graph)


    def solve(
        self,
        origin_id: int | set[int],
        destination_id: int = None,
        data_structure=BmsspDataStructure,
        pivot_relaxation_steps: int | None = None,
        target_tree_depth: int | None = None,
    ):
        """
        Function:

        - A Full BMSSP-style shortest path solver.
        - Return a dictionary of various path information including:
            - `id_path`: A list of node ids in the order they are visited
            - `path`: A list of node dictionaries (lat + long) in the order they are visited

        Required Arguments:

        - `origin_id`
            - Type: int | set of int
            - What: The id of the origin node from the graph dictionary to start the shortest path from
            - Note: If you pass a set, only the first id in the set will be checked for input validation
        - `destination_id`
            - Type: int | None
            - What: The id of the destination node from the graph dictionary to end the shortest path at
            - Note: If None, returns the distance matrix and predecessor list for the origin node
            - Note: If provided, returns the shortest path [origin_id, ..., destination_id] and its length

        Optional Arguments:

        - pivot_relaxation_steps:
            - Type: int | None
            - Default: ceil(log(len(graph), 2) ** (1 / 3))
            - What: The number of relaxation steps to perform when finding pivots (k). If None, it will be computed based on the graph size.
        - target_tree_depth:
            - Type: int | None
            - Default: int(log(len(graph), 2) ** (2 / 3))
            - What: The target depth of the search tree (t). If None, it will be computed based on the graph size.

        Returns:

        - A dictionary with the following keys
            - `origin_id`: The id of the origin node or a list of ids if a set was provided
            - `destination_id`: The id of the destination node (or None)
            - `predecessor`: The predecessor list for path reconstruction
            - `distance_matrix`: The distance matrix from the origin node to all other nodes
            - `path`: The shortest path from origin_id to destination_id (or None)
            - `length`: The length of the shortest path from origin_id to destination_id (or None)
        """
        if isinstance(origin_id, set):
            if len(origin_id) < 1:
                raise ValueError(
                    "Your provided origin_id set must have at least 1 node"
                )
            origin_id_check = next(iter(origin_id))
        else:
            origin_id_check = origin_id
        # Input Validation
        input_check(
            graph=self.graph, origin_id=origin_id_check, destination_id=destination_id
        )

        # Run the BMSSP Algorithm to relax as many edges as possible.
        solver = BmsspCore(
            self.constant_degree_dict["graph"], 
            origin_id, 
            data_structure=data_structure,
            pivot_relaxation_steps=pivot_relaxation_steps, 
            target_tree_depth=target_tree_depth
        )
        if destination_id is not None:
            if solver.distance_matrix[destination_id] == float("inf"):
                raise Exception(
                    "Something went wrong, the origin and destination nodes are not connected."
                )
            
        outputs = convert_from_constant_degree(
            distance_matrix=solver.distance_matrix,
            predecessor_matrix=solver.predecessor,
            constant_degree_dict=self.constant_degree_dict,
        )

        return {
            "origin_id": (
                origin_id if isinstance(origin_id, int) else list(origin_id)
            ),
            "destination_id": destination_id,
            "predecessor": outputs["predecessor_matrix"],
            "distance_matrix": outputs["distance_matrix"],
            "path": (
                reconstruct_path(
                    destination_id=destination_id, predecessor=outputs["predecessor_matrix"]
                )
                if destination_id
                else None
            ),
            "length": (
                outputs["distance_matrix"][destination_id] if destination_id else None
            ),
        }
