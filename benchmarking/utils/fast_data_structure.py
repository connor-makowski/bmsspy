from heapq import heappop, heappush, heapify

inf = float("inf")


class BmsspDataStructure:
    """
    A special data structure optimized to run fast on average-case scenarios when using Cpython.
    Not currently implemented since it does not necessarily outperform heapdict on PyPy.

    - This creates a min-heap of (value, key) pairs, allowing for efficient retrieval of the smallest values.
    - It supports insertion and batch insertion of key-value pairs.
    - When compared to heapdict when running pypy, this runs roughly equivalently.
    - When compared to heapdict when running cpython, this runs roughly 40% faster on average-case scenarios.

    Data structure for inserting, updating and pulling the M smallest key-value pairs
    together with a lower bound on the remaining values (or B if empty), as required by Alg. 3.
    """

    def __init__(self, subset_size: int, upper_bound: int | float, distance_matrix: list[int|float]):
        # subset_size: how many items to return per pull (must match Alg. 3 for level l -> Given as M)
        self.subset_size = max(1, subset_size)
        self.upper_bound = upper_bound
        self.distance_matrix = distance_matrix
        self.heap = []

    def insert_key_value(self, key: int, value: int | float):
        """
        Insert/refresh a key-value pair;
        """
        heappush(self.heap, (value, key))

    def is_empty(self) -> bool:
        """
        Check for empty data structure.
        """
        return len(self.heap) == 0

    def pull(self):
        """
        Return (remaining_best, subset) where subset is up to self.subset_size keys with *globally* smallest values.
        Remove the returned keys from the structure (matching Alg. 3 semantics).
        remaining_best is the smallest value still present after removal, or self.upper_bound if empty.
        """
        subset = set()
        count = 0

        while self.heap and count < self.subset_size:
            value, key = heappop(self.heap)
            if self.distance_matrix[key] == value:
                subset.add(key)
                count += 1

        # Ensure the remaining best is up-to-date
        remaining_best = self.upper_bound
        while self.heap:
            distance, key = self.heap[0]
            if self.distance_matrix[key] != distance:
                heappop(self.heap)
            elif key in subset:
                heappop(self.heap)
            else:
                remaining_best = distance
                break

        return remaining_best, subset

            

    def batch_prepend(self, key_value_pairs: set[tuple[int, int | float]]):
        """
        Insert/refresh multiple key-value pairs at once.
        """
        for key, value in key_value_pairs:
            heappush(self.heap, (value, key))
