from heapq import heappush, heappop
from math import ceil, log

from bmsspy.data_structures.data_structure import BmsspDataStructure
from bmsspy.helpers.utils import inf

from decimal import Decimal


def is_pivot(root: int, forest: dict[int, set[int]], threshold: int) -> bool:
    """
    Function:

    - Returns True if the number of reachable nodes meets or exceeds a given threshold.
    - Returns False otherwise.

    Required Arguments:

    - `root`
        - Type: int
        - What: The starting node for the DFS traversal.
    - `forest`
        - Type: dict[int, set[int]]
        - What: Adjacency list representing the directed forest.
    - `threshold`
        - Type: int
        - What: The minimum number of reachable nodes required to return True.
    """
    seen = set()
    stack = [root]
    cnt = 0
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        cnt += 1
        if cnt >= threshold:
            return True
        seen.add(x)
        stack.extend(forest[x])
    return False


class BmsspCore:
    def __init__(
        self,
        graph: list[dict[int, int | float]],
        origin_ids: set[int] | int,
        counter_value: int,
        edge_adj_graph: list[dict[int, int | float]],
        data_structure=BmsspDataStructure,
        pivot_relaxation_steps: int | None = None,
        target_tree_depth: int | None = None,
    ):
        """
        Function:

        - Initialize the BMSSP solver with a graph represented as an adjacency list.

        Required Arguments:

        - graph:
            - Type: list[dict[int, int | float]]
            - Description: The graph is represented as an adjacency list, where each node points to a dictionary of its neighbors and their edge weights.
            - Note: This graph should be in a max degree 2 (no more than two in connections and/or no more than two out connections per node) to function correctly.
        - origin_ids:
            - Type: set[int] | int
            - What: The IDs of the starting nodes for the BMSSP algorithm.
            - Note: Can be a single integer or a set of integers.
        - counter_value:
            - Type: int
            - What: The increment value (counter) added to the distance matrix to track how many edges have been traversed (used for unique path lengths).
                - Note: This should be set such that the maximum possible path length multiplied by counter_value is less than half of a single decimal place at the precision level.
        - edge_adj_graph:
            - Type: list[dict[int, int | float]]
            - What: The adjustment graph used to ensure unique path lengths.
                - Note: This should include edge id based adjustments.
                - Note: The largest edge id based adjustment should be less than half of the counter_value

        Optional Arguments:

        - data_structure:
            - Type: class
            - Default: BmsspDataStructure
            - What: The data structure class to be used for managing the frontier during the BMSSP algorithm.
        - pivot_relaxation_steps:
            - Type: int | None
            - Default: ceil(log(len(graph), 2) ** (1 / 3))
            - What: The number of relaxation steps to perform when finding pivots (k). If None, it will be computed based on the graph size.
        - target_tree_depth:
            - Type: int | None
            - Default: int(log(len(graph), 2) ** (2 / 3))
            - What: The target depth of the search tree (t). If None, it will be computed based on the graph size.
        """
        #################################
        # Initial checks and data setup
        #################################
        graph_len = len(graph)
        if graph_len < 2:
            raise ValueError("Your provided graph must have at least 2 nodes")
        if isinstance(origin_ids, int):
            origin_ids = {origin_ids}
        self.graph = graph
        self.counter_and_edge_distance_matrix = [inf] * graph_len
        self.counter_distance_matrix = [inf] * graph_len

        # Addition: Unique Path Adjustment Setup
        self.edge_adj_graph = edge_adj_graph
        self.counter_value = counter_value

        # Addition: Initialize Predecessor array for path reconstruction
        self.predecessor = [-1] * graph_len
        # Allow for arbitrary data structures
        self.data_structure = data_structure
        for origin_id in origin_ids:
            self.counter_and_edge_distance_matrix[origin_id] = Decimal(0)
            self.counter_distance_matrix[origin_id] = Decimal(0)

        #####################################
        # Practical choices (k and t) based on n
        #####################################
        # Calculate k
        # Modification: Use log base 2 to ensure everything is properly relaxed
        if pivot_relaxation_steps is not None:
            self.pivot_relaxation_steps = pivot_relaxation_steps
        else:
            self.pivot_relaxation_steps = int(log(graph_len, 2) ** (1 / 3))  # k
        assert (
            isinstance(self.pivot_relaxation_steps, int)
            and self.pivot_relaxation_steps > 0
        ), "pivot_relaxation_steps must be a positive integer"
        # Calculate t
        # Modification: Use log base 2 to ensure everything is properly relaxed
        if target_tree_depth is not None:
            self.target_tree_depth = target_tree_depth
        else:
            self.target_tree_depth = int(log(graph_len, 2) ** (2 / 3))  # t
        assert (
            isinstance(self.target_tree_depth, int)
            and self.target_tree_depth > 0
        ), "target_tree_depth must be a positive integer"

        #################################
        # Calculate l based on t
        #################################
        # Compute max_recursion_depth based on t
        # Modification: Use log base 2 to ensure everything is properly relaxed
        self.max_recursion_depth = ceil(
            log(graph_len, 2) / self.target_tree_depth
        )  # l

        #################################
        # Run the algorithm
        #################################
        # Run the solver algorithm
        upper_bound, frontier = self.recursive_bmssp(
            self.max_recursion_depth, inf, origin_ids
        )

    def find_pivots(
        self, upper_bound: int | float, frontier: set[int]
    ) -> tuple[set[int], set[int]]:
        """
        Function:

        - Finds pivot sets pivots and temp_frontier according to Algorithm 1.

        Required Arguments:

        - upper_bound:
            - Type: int | float
            - What: The upper bound threshold (B)
        - frontier:
            - Type: set[int]
            - What: Set of vertices (S)

        Optional Arguments:

        - None

        Returns:

        - pivots:
            - Type: Set[int]
            - What: Set of pivot vertices
        - frontier:
            - Type: Set[int]
            - What: Return a new frontier set of vertices within the upper_bound
        """
        temp_frontier = set(frontier)
        prev_frontier = set(frontier)

        # Multi-step limited relaxation from current frontier
        for _ in range(self.pivot_relaxation_steps):
            curr_frontier = set()
            for prev_frontier_idx in prev_frontier:
                prev_distance = self.counter_distance_matrix[prev_frontier_idx]
                for connection_idx, connection_distance in self.graph[
                    prev_frontier_idx
                ].items():
                    # Modification: Use a new get distance function to ensure unique lengths
                    new_distance = (
                        prev_distance
                        + connection_distance
                        + self.counter_value
                        + self.edge_adj_graph[prev_frontier_idx][connection_idx]
                    )
                    # Important: Allow equality on relaxations
                    if (
                        new_distance
                        <= self.counter_and_edge_distance_matrix[connection_idx]
                    ):
                        # Addition: Add predecessor tracking
                        if (
                            new_distance
                            < self.counter_and_edge_distance_matrix[
                                connection_idx
                            ]
                        ):
                            self.predecessor[connection_idx] = prev_frontier_idx
                            self.counter_and_edge_distance_matrix[
                                connection_idx
                            ] = new_distance
                            self.counter_distance_matrix[connection_idx] = (
                                prev_distance
                                + connection_distance
                                + self.counter_value
                            )
                        if new_distance < upper_bound:
                            curr_frontier.add(connection_idx)
            temp_frontier.update(curr_frontier)
            prev_frontier = curr_frontier
            # If the search balloons, take the current frontier as pivots
            if len(temp_frontier) > self.pivot_relaxation_steps * len(frontier):
                pivots = set(frontier)
                return pivots, temp_frontier

        # Build tight-edge forest F on temp_frontier: edges (u -> v) with db[u] + w == db[v]
        forest = {i: set() for i in temp_frontier}
        indegree = {i: 0 for i in temp_frontier}
        for frontier_idx in temp_frontier:
            # prev_distance = self.counter_distance_matrix[frontier_idx]
            for connection_idx, connection_distance in self.graph[
                frontier_idx
            ].items():
                # Modification: Use predecessor tracking instead of distance comparison
                if self.predecessor[connection_idx] == frontier_idx:
                    if connection_idx in temp_frontier:
                        # direction is frontier_idx -> connection_idx (parent to child)
                        forest[frontier_idx].add(connection_idx)
                        indegree[connection_idx] += 1

        pivots = set()
        for frontier_idx in frontier:
            if indegree.get(frontier_idx, 0) == 0:
                if is_pivot(
                    frontier_idx,
                    forest=forest,
                    threshold=self.pivot_relaxation_steps,
                ):
                    pivots.add(frontier_idx)

        return pivots, temp_frontier

    def base_case(
        self, upper_bound: int | float, frontier: set[int]
    ) -> tuple[int | float, set[int]]:
        """
        Function:

        - Implements Algorithm 2: Base Case of BMSSP

        Required Arguments:
        - upper_bound:
            - Type: int | float
        - frontier:
            - Type: set
            - What: Set with a single vertex x (complete)

        Returns:
        - new_upper_bound:
            - Type: int | float
            - What: The new upper bound for the search
        - new_frontier:
            - Type: set[int]
            - What: Set of vertices v such that distance_matrix[v] < new_upper_bound
        """
        assert len(frontier) == 1, "Frontier must be a singleton set"
        first_frontier = next(iter(frontier))

        new_frontier = set()
        heap = []
        heappush(
            heap,
            (
                self.counter_and_edge_distance_matrix[first_frontier],
                first_frontier,
            ),
        )
        new_upper_bound = upper_bound
        # Grow until we exceed pivot_relaxation_steps (practical limit), as in Algorithm 2
        while heap:
            frontier_distance, frontier_idx = heappop(heap)
            # Modification: instead of the post process, just break early
            if len(new_frontier) >= self.pivot_relaxation_steps:
                new_upper_bound = frontier_distance
                break
            new_frontier.add(frontier_idx)
            prev_distance = self.counter_distance_matrix[frontier_idx]
            for connection_idx, connection_distance in self.graph[
                frontier_idx
            ].items():
                # Modification:
                new_distance = (
                    prev_distance
                    + connection_distance
                    + self.counter_value
                    + self.edge_adj_graph[frontier_idx][connection_idx]
                )
                if (
                    new_distance
                    <= self.counter_and_edge_distance_matrix[connection_idx]
                    and new_distance < upper_bound
                ):
                    # Addition: Add predecessor tracking
                    if (
                        new_distance
                        < self.counter_and_edge_distance_matrix[connection_idx]
                    ):
                        self.predecessor[connection_idx] = frontier_idx
                        self.counter_and_edge_distance_matrix[
                            connection_idx
                        ] = new_distance
                        self.counter_distance_matrix[connection_idx] = (
                            prev_distance
                            + connection_distance
                            + self.counter_value
                        )
                    heappush(heap, (new_distance, connection_idx))

        return new_upper_bound, new_frontier

    def recursive_bmssp(
        self, recursion_depth: int, upper_bound: int | float, frontier: set[int]
    ) -> tuple[int | float, set[int]]:
        """
        Function:

        - Implements Algorithm 3: Bounded Multi-Source Shortest Path (BMSSP)

        Required Arguments:

        - recursion_depth:
            - Type: int
            - What: The depth of the recursion
        - upper_bound:
            - Type: float
            - What: The upper bound for the search
        - frontier:
            - Type: set[int]
            - What: The set of vertices to explore

        Returns:

        - new_upper_bound:
            - Type: int | float
            - What: The new upper bound for the search
        - new_frontier:
            - Type: set[int]
            - What: Set of vertices v such that distance_matrix[v] < new_upper_bound
        """
        # Base case
        if recursion_depth == 0:
            new_upper_bound, new_frontier = self.base_case(
                upper_bound, frontier
            )
            return new_upper_bound, new_frontier

        # Step 4: Find pivots and temporary frontier
        pivots, temp_frontier = self.find_pivots(upper_bound, frontier)

        # Step 5–6: initialize data_struct with pivots
        # subset_size = 2^((l-1) * t)
        subset_size = 2 ** ((recursion_depth - 1) * self.target_tree_depth)
        data_struct = self.data_structure(
            subset_size=subset_size, upper_bound=upper_bound
        )
        for p in pivots:
            data_struct.insert_key_value(
                p, self.counter_and_edge_distance_matrix[p]
            )

        # Track new_frontier and B' according to Algorithm 3
        new_frontier = set()
        # Store the completion_bound for use if the frontier is empty and we break early
        completion_bound = min(
            (self.counter_and_edge_distance_matrix[p] for p in pivots),
            default=upper_bound,
        )

        # Work budget that scales with level: k*2**(l*t)
        # k = self.pivot_relaxation_steps
        # t = self.target_tree_depth
        work_budget = self.pivot_relaxation_steps * 2 ** (
            recursion_depth * self.target_tree_depth
        )
        # Main loop
        while len(new_frontier) < work_budget and not data_struct.is_empty():
            # Step 10: Pull from data_struct: get data_struct_frontier_temp and upper_bound_i
            data_struct_frontier_bound_temp, data_struct_frontier_temp = (
                data_struct.pull()
            )

            # Step 11: Recurse on (l-1, data_struct_frontier_bound_temp, data_struct_frontier_temp)
            completion_bound, new_frontier_temp = self.recursive_bmssp(
                recursion_depth - 1,
                data_struct_frontier_bound_temp,
                data_struct_frontier_temp,
            )

            # Track results
            new_frontier.update(new_frontier_temp)

            # Step 13: Initialize intermediate_frontier to batch-prepend
            intermediate_frontier = set()

            # Step 14–20: relax edges from new_frontier_temp and enqueue into D or intermediate_frontier per their interval
            for new_frontier_idx in new_frontier_temp:
                prev_distance = self.counter_distance_matrix[new_frontier_idx]
                for connection_idx, connection_distance in self.graph[
                    new_frontier_idx
                ].items():
                    new_distance = (
                        prev_distance
                        + connection_distance
                        + self.counter_value
                        + self.edge_adj_graph[new_frontier_idx][connection_idx]
                    )
                    if (
                        new_distance
                        <= self.counter_and_edge_distance_matrix[connection_idx]
                    ):
                        # Addition: Add predecessor tracking
                        if (
                            new_distance
                            < self.counter_and_edge_distance_matrix[
                                connection_idx
                            ]
                        ):
                            self.predecessor[connection_idx] = new_frontier_idx
                            self.counter_and_edge_distance_matrix[
                                connection_idx
                            ] = new_distance
                            self.counter_distance_matrix[connection_idx] = (
                                prev_distance
                                + connection_distance
                                + self.counter_value
                            )
                        # Insert based on which interval the new distance falls into
                        if (
                            data_struct_frontier_bound_temp
                            <= new_distance
                            < upper_bound
                        ):
                            data_struct.insert_key_value(
                                connection_idx, new_distance
                            )
                        elif (
                            completion_bound
                            <= new_distance
                            < data_struct_frontier_bound_temp
                        ):
                            intermediate_frontier.add(
                                (connection_idx, new_distance)
                            )

            # Step 21: Batch prepend intermediate_frontier plus filtered data_struct_frontier_temp in completion_bound, data_struct_frontier_bound_temp)
            data_struct_frontier_temp_filtered = {
                (x, self.counter_and_edge_distance_matrix[x])
                for x in data_struct_frontier_temp
                if completion_bound
                <= self.counter_and_edge_distance_matrix[x]
                < data_struct_frontier_bound_temp
            }

            data_struct.batch_prepend(
                intermediate_frontier | data_struct_frontier_temp_filtered
            )
        # Optional code if you do not have guaranteed unique lengths.
        # if len(new_frontier) > work_budget:
        #     completion_bound = pivot_completion_bound

        # Step 22: Final return
        completion_bound = min(completion_bound, upper_bound)
        new_frontier = new_frontier | {
            v
            for v in temp_frontier
            if self.counter_and_edge_distance_matrix[v] < completion_bound
        }

        return completion_bound, new_frontier
