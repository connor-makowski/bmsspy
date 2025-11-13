from .core import BmsspCore
from .helpers.utils import input_check, reconstruct_path, convert_to_constant_degree, convert_from_constant_degree, inf

from bmsspy.data_structures.data_structure import BmsspDataStructure
from decimal import Decimal
from math import ceil, log

class Bmssp:
    def __init__(self, graph: list[dict[int, int | float]], precision: int = 6, use_constant_degree_graph: bool = True):
        """
        Function:

        - Initialize a BMSSP-style shortest path object that can execute a bmssp solve method.
        - Calculates and stores necessary variables for unique path length adjustments.
        - Optionally calculate the constant degree graph and related info.

        Required Arguments:

        - `graph`:
            - Type: list of dictionaries
            - What: The input graph represented as a list of dictionaries where each index represents a node id.
                    Each dictionary contains neighboring node ids as keys and edge weights as values.

        Optional Arguments:

        - `precision`:
            - Type: int
            - Default: 6
            - What: The decimal precision to round edge weights to for calculations
                - Note: This is necessary to ensure that the unique values added to each edge weight do not cause issues with expected returned path lengths.
        - `use_constant_degree_graph`:
            - Type: bool
            - Default: True
            - What: Whether to convert the input graph to a constant degree graph to match the original BMSSP algorithm requirements.
            - Note: It appears that this is not necessary for solving the algorithm, but is used to achieve big O complexity targets.
                    This is default to True even though it appears to be slower in practice for all the graphs we have tested thus far.
        """
        self.graph = [{k: round(Decimal(v), precision) for k, v in i.items()} for i in graph]
        self.precision = precision
        self.use_constant_degree_graph = use_constant_degree_graph

        if self.use_constant_degree_graph:
            self.constant_degree_dict = convert_to_constant_degree(self.graph)
            self.used_graph = self.constant_degree_dict["graph"]
        else:
            self.used_graph = self.graph

        ######################
        # Unique Path Length Adjustment Setup
        ######################
        # Create an adjustment graph to allow for guaranteed unique path lengths
        # This essentially adds a combination of small increments to each edge weight
        #   to ensure that no two paths are measured as the same length
        num_edges = sum(len(neighbors) for neighbors in self.used_graph)
        num_nodes = len(self.used_graph)
        counter_magnitude_adjustment = -ceil(log((Decimal(num_nodes*2+1))/(Decimal(10)**Decimal(-self.precision-1)),10))
        self.counter_value = Decimal(10)**Decimal(counter_magnitude_adjustment)
        edge_id_magnitude_adjustment = -ceil(log(((Decimal(num_edges*2+1))/(self.counter_value)),10))
        edge_id_adjustment_value = Decimal(10)**Decimal(edge_id_magnitude_adjustment)

        # Store a set of adjustment values to be used during BMSSP solving
        edge_id_value = Decimal(0.0)
        self.edge_adj_graph = [{} for _ in range(len(self.used_graph))]
        for node_idx, node_neighbors in enumerate(self.used_graph):
            for neighbor in node_neighbors:
                edge_id_value += edge_id_adjustment_value
                self.edge_adj_graph[node_idx][neighbor] = edge_id_value


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
        # Input Validation (Uses original graph and not used_graph to ensure validity)
        input_check(
            graph=self.graph, origin_id=origin_id_check, destination_id=destination_id
        )

        # Run the BMSSP Algorithm to relax as many edges as possible.
        solver = BmsspCore(
            graph = self.used_graph,
            origin_ids = origin_id,
            counter_value=self.counter_value,
            edge_adj_graph=self.edge_adj_graph,
            data_structure=data_structure,
            pivot_relaxation_steps=pivot_relaxation_steps, 
            target_tree_depth=target_tree_depth
        )
        if destination_id is not None:
            if solver.counter_distance_matrix[destination_id] == float("inf"):
                raise Exception(
                    "Something went wrong, the origin and destination nodes are not connected."
                )
        
        if self.use_constant_degree_graph:
            converted_outputs = convert_from_constant_degree(
                distance_matrix=solver.counter_distance_matrix,
                predecessor_matrix=solver.predecessor,
                constant_degree_dict=self.constant_degree_dict,
            )
            predecessor = converted_outputs["predecessor_matrix"]
            distance_matrix = converted_outputs["distance_matrix"]
        else:
            predecessor = solver.predecessor
            distance_matrix = solver.counter_distance_matrix

        # Remove counter values from distance matrix
        distance_matrix = [round(i, self.precision) if i != inf else i for i in distance_matrix]

        return {
            "origin_id": (
                origin_id if isinstance(origin_id, int) else list(origin_id)
            ),
            "destination_id": destination_id,
            "predecessor": predecessor,
            "distance_matrix": distance_matrix,
            "path": (
                reconstruct_path(
                    destination_id=destination_id, predecessor=predecessor
                )
                if destination_id
                else None
            ),
            "length": (
                distance_matrix[destination_id] if destination_id else None
            ),
        }
