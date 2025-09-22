# Note: This median function breaks the big O (see: https://github.com/python/cpython/issues/65791)
from statistics import median_high
from .rbtree import RBTree

inf = float("inf")


class LinkedListNode:
    def __init__(self, key=None, value=None, parent_list=None):
        self.key = key
        self.value = value
        self.parent_list = (
            parent_list  # Pointer to the linked list this node belongs to
        )
        self.next = None
        self.prev = None

    def __str__(self):
        return f"({self.value})"


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0
        self.prev_list = (
            None  # Pointer to the previous linked list in the chain
        )
        self.next_list = None  # Pointer to the next linked list in the chain

    def __iter__(self):
        current = self.head
        while current:
            yield current
            current = current.next

    def append(self, key, value):
        new_node = LinkedListNode(key, value, self)
        self.size += 1
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def remove(self, node):
        if node.parent_list != self:
            raise ValueError("Node does not belong to this linked list.")
        self.size -= 1
        if node.prev:
            node.prev.next = node.next
        if node.next:
            node.next.prev = node.prev
        if node == self.head:
            self.head = node.next
        if node == self.tail:
            self.tail = node.prev

    def is_empty(self):
        return self.size <= 0

    def __str__(self):
        str = (
            "->".join(f"({node.key},{node.value})" for node in self)
            + "\n"
            # + self.next_list.__str__()
            # if self.next_list is not None
            # else ""
        )
        return str


class BmsspDataStructure:
    """
    Data structure for inserting, updating and pulling the M smallest key-value pairs
    together with a lower bound on the remaining values (or B if empty), as required by Alg. 3.
    """

    def __init__(self, subset_size: int, upper_bound: int | float):
        # subset_size: how many items to return per pull (must match Alg. 3 for level l -> Given as M)
        self.subset_size = max(2, subset_size)
        self.pull_size = max(1, subset_size)
        self.upper_bound = upper_bound
        self.keys = (
            {}
        )  # maps keys to their linked list node and which linked list they are in (0 for D0, 1 for D1)
        self.D0 = LinkedList()  # D0 is a linked list of linked lists
        self.D1 = (
            RBTree()
        )  # D1 is a RB tree tracking upper bounds of linked lists
        list = LinkedList()
        self.D1.insert(
            self.upper_bound, list
        )  # Start with one empty linked list with upper bound B

    def delete_d1(self, key):
        if key not in self.keys:
            raise ValueError("Key not found in data structure.")
        list_node = self.keys.pop(key)[0]
        linked_list = list_node.parent_list
        # Remove the key-value pair from the linked list
        linked_list.remove(list_node)
        # If the linked list is empty, remove it from D1
        if linked_list.is_empty():
            block = self.D1.find(list_node.value, target="upper")
            if (
                block.key != self.upper_bound
            ):  # allow the upper bound block to remain even if empty
                if linked_list.prev_list:
                    linked_list.prev_list.next_list = linked_list.next_list
                if linked_list.next_list:
                    linked_list.next_list.prev_list = linked_list.prev_list
                if (
                    block.val == linked_list
                ):  # Only remove if it hasn't been replaced
                    self.D1.remove(block.key)
                else:
                    raise ValueError(
                        "Linked list not found in RBTree (probably due to a key collision)."
                    )
                del linked_list  # Just to be explicit

    def delete_d0(self, key):
        if key not in self.keys:
            return
        list_node = self.keys.pop(key)[0]
        linked_list = list_node.parent_list
        linked_list.remove(list_node)
        if linked_list.is_empty():
            # Remove the linked list from the chain
            if linked_list.prev_list:
                linked_list.prev_list.next_list = linked_list.next_list
            if linked_list.next_list:
                linked_list.next_list.prev_list = linked_list.prev_list
            if linked_list == self.D0:
                self.D0 = linked_list.next_list
            del linked_list  # Just to be explicit

    def insert_key_value(self, key: int, value: int | float):
        """
        Insert/refresh a key-value pair;
        """
        # If the key already exists, see if we need to remove it first
        if key in self.keys:
            item = self.keys[key]
            if item[0].value < value:
                return  # No need to update if the new value is not lower
            elif item[1] == 0:
                self.delete_d0(key)
            else:
                self.delete_d1(key)
        # Insert the new key-value pair in D1
        block = self.D1.find(value, target="upper")
        if block is None:
            raise ValueError(
                "No suitable linked list found in D1, this means an incorrect upper bound was set."
            )
        linked_list = block.val
        linked_list.append(key, value)
        self.keys[key] = (linked_list.tail, 1)  # Update with the new node

        # If the linked list exceeds the subset size, perform a split
        if linked_list.size > self.subset_size:
            self.split(linked_list, block.key)

    def split(self, linked_list, upper_bound):
        median_value = median_high(node.value for node in linked_list)
        if (
            median_value == upper_bound
        ):  # Don't split if new block would have the same upper bound
            return
        new_list = LinkedList()
        max_value = -inf
        # Move nodes with value < median_value to the new linked list to preserve original upper bound
        for node in linked_list:
            if node.value < median_value:
                if node.value > max_value:
                    max_value = node.value
                new_list.append(node.key, node.value)
                self.keys[node.key] = (
                    new_list.tail,
                    1,
                )  # Update with the new node
                linked_list.remove(node)

        if new_list.is_empty():
            # Sometimes the new list would have been all median values, in which case we don't need to split
            return
        # Update D1 with the new linked list
        new_list.next_list = linked_list
        new_list.prev_list = linked_list.prev_list
        if linked_list.prev_list:
            linked_list.prev_list.next_list = new_list
        linked_list.prev_list = new_list
        self.D1.insert(max_value, new_list)
        if linked_list.is_empty():
            raise ValueError("Linked list should not be empty after split.")

    def batch_prepend(self, key_value_pairs: list[tuple[int, int | float]]):
        """
        Insert/refresh multiple key-value pairs at once.
        """
        min_pairs = {}
        for key, value in key_value_pairs:
            if key not in min_pairs or value < min_pairs[key]:
                if key in self.keys:
                    item = self.keys[key]
                    if item[0].value < value:
                        continue  # No need to update if the new value is not lower
                    elif item[1] == 0:
                        self.delete_d0(key)
                    else:
                        self.delete_d1(key)
                min_pairs[key] = value
        if len(min_pairs) == 0:
            return
        elif len(min_pairs) <= self.subset_size:
            # If we are small enough, just insert them all as a block
            old_head = self.D0
            self.D0 = LinkedList()
            self.D0.next_list = old_head
            old_head.prev_list = self.D0
            for key, value in min_pairs.items():
                self.D0.append(key, value)
                self.keys[key] = (self.D0.tail, 0)
        else:
            # Otherwise, split by median and try again. (note that the lower half goes in last to preserve order)
            # Iterative approach to batch prepend
            stack = [list(min_pairs.items())]  # Start with all key-value pairs
            while stack:
                current_pairs = stack.pop()
                if len(current_pairs) <= self.subset_size:
                    # Small enough to insert as a block
                    old_head = self.D0
                    self.D0 = LinkedList()
                    self.D0.next_list = old_head
                    if old_head:
                        old_head.prev_list = self.D0
                    # Add all pairs to the new block
                    for key, value in current_pairs:
                        self.D0.append(key, value)
                        self.keys[key] = (self.D0.tail, 0)
                else:
                    # Split by median
                    values = [value for _, value in current_pairs]
                    median = median_high(values)

                    # Split into upper and lower halves
                    upper_list = []
                    lower_list = []
                    for key, value in current_pairs:
                        if value < median:
                            lower_list.append((key, value))
                        elif value > median:
                            upper_list.append((key, value))
                        else:
                            # Equal to median, distribute evenly
                            if len(lower_list) <= len(upper_list):
                                lower_list.append((key, value))
                            else:
                                upper_list.append((key, value))

                    # Push lower list first so it gets processed last (to preserve order)
                    if lower_list:
                        stack.append(lower_list)
                    if upper_list:
                        stack.append(upper_list)

    def pull(self):
        """
        Return (remaining_best, subset) where subset is up to self.subset_size keys with *globally* smallest values.
        Remove the returned keys from the structure (matching Alg. 3 semantics).
        remaining_best is the smallest value still present after removal, or self.upper_bound if empty.
        """

        smallest_d0 = set()
        if self.D0 and not self.D0.is_empty():
            current_list = self.D0
            # First create the set - we don't know if we will need all of them yet so don't remove
            while (
                len(smallest_d0) < self.subset_size and current_list is not None
            ):
                for item in current_list:
                    smallest_d0.add(item.key)
                current_list = current_list.next_list
        smallest_d1 = set()
        if self.D1.root is not None:
            current_list = self.D1.get_min(self.D1.root).val
            while (
                len(smallest_d1) < self.subset_size and current_list is not None
            ):
                for item in current_list:
                    smallest_d1.add(item.key)
                current_list = current_list.next_list
        # Now combine the two sets to get the final subset
        # TODO: implement an O(M) merge instead of sorting (see same github issue as above)
        combined = list(smallest_d0) + list(smallest_d1)
        combined.sort(key=lambda k: self.keys[k][0].value)
        subset = combined[: self.pull_size]
        for key in subset:
            # Now remove the selected keys from the structure
            if key in self.keys:
                if self.keys[key][1] == 0:
                    self.delete_d0(key)
                else:
                    self.delete_d1(key)
        # Compute lower bound for remaining
        remaining_best = self.upper_bound
        if self.D0 and not self.D0.is_empty():
            remaining_best = min(
                remaining_best, min(node.value for node in self.D0)
            )
        smallest_block = self.D1.get_min(self.D1.root)
        if smallest_block is not None and smallest_block.val.size > 0:
            remaining_best = min(
                remaining_best,
                min(node.value for node in smallest_block.val),
            )
        return remaining_best, set(subset)

    def is_empty(self) -> bool:
        """
        Check for empty data structure.
        """
        return len(self.keys) == 0
