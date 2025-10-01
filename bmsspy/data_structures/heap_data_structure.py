from bmsspy.helpers.heapdict import heapdict

inf = float("inf")


class BmsspDataStructure:
    """
    Data structure for inserting, updating and pulling the M smallest key-value pairs
    together with a lower bound on the remaining values (or B if empty), as required by Alg. 3.
    """

    def __init__(self, subset_size: int, upper_bound: int | float):
        # subset_size: how many items to return per pull (must match Alg. 3 for level l -> Given as M)
        self.subset_size = max(1, subset_size)
        self.upper_bound = upper_bound
        self.heap = heapdict()

    def insert_key_value(self, key: int, value: int | float):
        """
        Insert/refresh a key-value pair;
        """
        if value < self.heap.get(key, inf):
            self.heap[key] = value

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

        # Take up to M distinct current keys
        while count < self.subset_size:
            key = self.heap.popitem()[0] if self.heap else None
            if key is None:
                break
            subset.add(key)
            count += 1

        # Compute lower bound for remaining
        if self.heap:
            remaining_best = self.heap.peekitem()[1]
        else:
            remaining_best = self.upper_bound
        return remaining_best, subset

    def batch_prepend(self, key_value_pairs: set[tuple[int, int | float]]):
        """
        Insert/refresh multiple key-value pairs at once.
        """
        for key, value in key_value_pairs:
            if value < self.heap.get(key, inf):
                self.heap[key] = value
