# This file was originally based off of: https://github.com/leryss/py-redblacktree
# See the LICENSE file for the original license: https://github.com/leryss/py-redblacktree/blob/main/LICENSE
# This file has been modified significantly for use in this project


class BSNode:
    def __init__(self, key: any, value: any = None):
        """
        Function:

        - Initialize a binary search tree node with a key and a value.

        Required Parameters:

        - key: The key associated with the node.
            - What: Any data type that supports comparison operations.
            - Why: Used to maintain the binary search tree property.
            - Example: An integer, string, or custom object with comparison methods.

        Optional Parameters:

        - value: The value associated with the node.
            - What: Any data type.
            - Why: Stores the data or information related to the key.
            - Default: None

        """
        self.key: any = key
        self.val: any = value
        self.parent: BSNode | None = None
        self.left: BSNode | None = None
        self.right: BSNode | None = None

    def num_nodes(self) -> int:
        """
        Function:

        - Count the number of nodes in the subtree rooted at this node.

        Returns:

        - int: The total number of nodes in the subtree.
        """
        return (
            1
            + (self.left.num_nodes() if self.left else 0)
            + (self.right.num_nodes() if self.right else 0)
        )


class BSTree:
    def __init__(self):
        """
        Function:

        - Initialize an empty binary search tree.
        """
        self.root: BSNode | None = None

    def insert(self, key: any, value: any = None) -> None:
        """
        Function:

        - A placeholder method for inserting a key-value pair into the binary search tree.
        - Note: This method is not implemented in the base class and should be overridden in subclasses.
        """
        raise Exception("Not implemented")

    def remove(self, key: any) -> None:
        """
        Function:

        - A placeholder method for removing a node with the specified key from the binary search tree.
        - Note: This method is not implemented in the base class and should be overridden in subclasses
        """
        raise Exception("Not implemented")

    def find(self, key: any, target: str = "exact") -> BSNode:
        """
        Function:

        - Find a node in the binary search tree based on the specified key and target type.

        Required Parameters:

        - key: The key to search for in the tree.
            - What: Any data type that supports comparison operations.
            - Why: Used to locate the desired node in the tree.
            - Example: An integer, string, or custom object with comparison methods.

        Opional Parameters:

        - target: The type of search to perform. Options are 'exact', 'upper', or 'lower'.
            - What: A string indicating the search type.
            - Why: Determines how the search is conducted.
            - Default: 'exact'
            - Options:
                - 'exact': Find the node with the exact key.
                - 'upper': Find the smallest node with a key greater than or equal to the specified key.
                - 'lower': Find the largest node with a key less than or equal to the specified key.

        Returns:

        - BSNode | None: The found node based on the search criteria, or None if no such node exists.

        """
        if not self.root:
            return None
        node = self.__find_fuzzy__(self.root, key)
        if target == "exact":
            if node.key == key:
                return node
            else:
                return None
        elif target == "upper":
            if node.key >= key:
                return node
            while node.parent:
                node = node.parent
                if node.key >= key:
                    return node
            return None
        elif target == "lower":
            if node.key <= key:
                return node
            while node.parent:
                node = node.parent
                if node.key <= key:
                    return node
            return None
        else:
            raise Exception("Invalid target for find")

    def get_max(self, node: BSNode) -> BSNode:
        """
        Function:

        - Find the maximum node in the subtree rooted at the given node.

        Required Parameters:

        - node: The root node of the subtree to search.
            - What: A BSNode instance.
            - Why: Used to locate the maximum node in the subtree.
            - Example: The root node of the subtree.

        Returns:

        - BSNode | None: The maximum node in the subtree, or None if the subtree is empty.
        """
        if node.right:
            return self.get_max(node.right)
        return node

    def get_min(self, node: BSNode) -> BSNode:
        """
        Function:

        - Find the minimum node in the subtree rooted at the given node.

        Required Parameters:

        - node: The root node of the subtree to search.
            - What: A BSNode instance.
            - Why: Used to locate the minimum node in the subtree.
            - Example: The root node of the subtree.

        Returns:

        - BSNode | None: The minimum node in the subtree, or None if the subtree is empty.
        """
        if node.left:
            return self.get_min(node.left)
        return node

    def __getitem__(self, key: any, default=None) -> any:
        """
        Function:

        - Retrieve the value associated with the specified key in the binary search tree.
        - Note: This method allows for dictionary-like access to the tree's values.
        - Note: This method requires an exact match for the key.

        Required Parameters:

        - key: The key to search for in the tree.
            - What: Any data type that supports comparison operations.
            - Why: Used to locate the desired node in the tree.
            - Example: An integer, string, or custom object with comparison methods.

        Optional Parameters:

        - default: The value to return if the key is not found in the tree.
            - What: Any data type.
            - Why: Provides a fallback value when the key is absent.
            - Default: None

        Returns:

        - any | None: The value associated with the key, or None if the key is not found.
        """

        node = self.find(key) if self.root else None
        return node.val if node else default

    def __len__(self) -> int:
        """
        Function:

        - Get the number of nodes in the binary search tree.

        Returns:

        - int: The total number of nodes in the tree.
        """
        return self.root.num_nodes() if self.root else 0

    def __find_fuzzy__(self, node: BSNode, key: any) -> BSNode:
        """
        Function:

        - A helper method to find an equivalent (or adjacent) node to the specified key in the binary search tree.

        Required Parameters:

        - node: The current node to start the search from.
            - What: A BSNode instance.
            - Why: Used as the starting point for the search.
            - Example: The root node of the tree.
        - key: The key to search for in the tree.
            - What: Any data type that supports comparison operations.
            - Why: Used to locate the closest node in the tree.
            - Example: An integer, string, or custom object with comparison methods.

        Returns:

        - BSNode: The found node that is either equivalent to or adjacent to the specified key.
        """
        if key < node.key:
            return self.__find_fuzzy__(node.left, key) if node.left else node
        elif key > node.key:
            return self.__find_fuzzy__(node.right, key) if node.right else node
        return node

    def __insert_node__(self, start: BSNode, to_insert: BSNode) -> bool:
        """
            Inserts a given node (not value) into the tree without any rebalancing.
            Returns True if was inserted False if it was updated

        Function:

        - A helper method to insert a node into the binary search tree without rebalancing.

        Required Parameters:

        - start: The node to start the insertion from (usually the root).
            - What: A BSNode instance.
            - Why: Used as the starting point for the insertion.
            - Example: The root node of the tree.
        - to_insert: The node to be inserted into the tree.
            - What: A BSNode instance.
            - Why: The node that needs to be added to the tree.
            - Example: A new node with a key and value.

        Returns:

        - bool: True if the node was inserted, False if an existing node was updated.
        """

        def insert_internal(current_node):
            if to_insert.key < current_node.key:
                if current_node.left:
                    return insert_internal(current_node.left)

                current_node.left = to_insert
                to_insert.parent = current_node
                return True

            elif to_insert.key > current_node.key:
                if current_node.right:
                    return insert_internal(current_node.right)

                current_node.right = to_insert
                to_insert.parent = current_node
                return True

            current_node.val = to_insert.val
            return False

        if not self.root:
            self.root = to_insert
        else:
            return insert_internal(start)

    def __rotate_right__(self, y: BSNode) -> None:
        """
          T0   T0                         T0   T0
            \\ /                             \\ /
             y                               x
            / \\     right Rotation          /  \\
           x   T3   - - - - - - - >        T1   y
          / \\       < - - - - - - -            / \\
         T1  T2     left Rotation            T2  T3
        """
        x = y.left

        # Attach T2 to y
        T2 = x.right
        if T2:
            T2.parent = y
        y.left = T2

        # Attach x to T0
        if y == self.root:
            self.root = x
            x.parent = None
        else:
            T0 = y.parent
            if T0.left == y:
                T0.left = x
            else:
                T0.right = x
            x.parent = T0

        # Attach y to x
        y.parent = x
        x.right = y

    def __rotate_left__(self, x: BSNode) -> None:
        """
          T0   T0                         T0   T0
            \\ /                             \\ /
             y                               x
            / \\     right Rotation          /  \\
           x   T3   - - - - - - - >        T1   y
          / \\       < - - - - - - -            / \\
         T1  T2     left Rotation            T2  T3
        """

        y = x.right

        # Attach T2 to x
        T2 = y.left
        if T2:
            T2.parent = x
        x.right = T2

        if x == self.root:
            self.root = y
            y.parent = None
        else:
            # Attach T0 to y
            T0 = x.parent
            if T0.left == x:
                T0.left = y
            else:
                T0.right = y
            y.parent = T0

        # Attach x to y
        x.parent = y
        y.left = x


class RBNode(BSNode):
    def __init__(self, key: any, value: any, color: bool):
        """
        Function:

        - Initialize a red-black tree node with a key, value, and color.

        Required Parameters:

        - key: The key associated with the node.
            - What: Any data type that supports comparison operations.
            - Why: Used to maintain the binary search tree property.
            - Example: An integer, string, or custom object with comparison methods.
        - color: The color of the node (True for red, False for black).
            - What: A boolean value.
            - Why: Used to maintain the red-black tree properties.
            - Example: True (red) or False (black).

        Optional Parameters:

        - value: The value associated with the node.
            - What: Any data type.
            - Why: Stores the data or information related to the key.
            - Default: None
        """
        super().__init__(key, value)
        self.colored = color


class RBTreeRebalance:
    """
    A class that provides rebalancing methods for a Red-Black Tree.

    This is used primarily for code organization and clarity.
    """

    def __rebalance_ll__(self, gparent, parent):
        self.__rotate_right__(gparent)
        gparent.colored = not gparent.colored
        parent.colored = not parent.colored

        return parent

    def __rebalance_lr__(self, gparent, parent):
        node = parent.right
        self.__rotate_left__(parent)
        return self.__rebalance_ll__(gparent, node)

    def __rebalance_rl__(self, gparent, parent):
        node = parent.left
        self.__rotate_right__(parent)
        return self.__rebalance_rr__(gparent, node)

    def __rebalance_rr__(self, gparent, parent):
        self.__rotate_left__(gparent)
        gparent.colored = not gparent.colored
        parent.colored = not parent.colored

        return parent

    def __rebalance__(self, node):
        parent = node.parent
        if not parent or node.colored or parent.colored:
            return

        grandparent = parent.parent
        if not grandparent:
            return

        dir_parent = (
            self.left_idx if grandparent.left == parent else self.right_idx
        )
        uncle = (
            grandparent.right
            if dir_parent == self.left_idx
            else grandparent.left
        )

        if uncle and not uncle.colored:
            uncle.colored = parent.colored = True
            grandparent.colored = grandparent == self.root
            self.__rebalance__(grandparent)
        else:
            dir_node = self.left_idx if parent.left == node else self.right_idx
            self.__rebalance__(
                self.rotations[dir_parent][dir_node](grandparent, parent)
            )


class RBTreeFixup:
    """
    A class that provides fixup methods for a Red-Black Tree after deletion.
    This is used primarily for code organization and clarity.
    """

    def __fixup_left_1__(self, node, parent, sibling):
        """
        Sibling is red
            b               r                 b
          /   \\           /   \\             /   \\
        node   r    =>   b      y     =>   r      y
             /   \\      /  \\              /  \\
            x     y   node  x           node  x
        Solution: rotate parent left. swap colors between parent and sibling and continue
        """
        sibling.colored = True
        parent.colored = False
        self.__rotate_left__(parent)
        self.__remove_fixup__(node)

    def __fixup_right_1__(self, node, parent, sibling):
        """Mirror left case 1"""
        sibling.colored = True
        parent.colored = False
        self.__rotate_right__(parent)
        self.__remove_fixup__(node)

    def __fixup_left_2__(self, node, parent, sibling):
        """
            ?               b              ?
          /   \\           /   \\          /   \\
        node   b    =>   ?     r  =>    b     b
             /   \\      /  \\           /  \\
            x     r   node  x        node  x
        Solution: switch colors between parent and sibling then rotate parent left and color nephew black
        """
        sibling.colored = parent.colored
        parent.colored = True
        sibling.right.colored = True
        self.__rotate_left__(parent)

    def __fixup_right_2__(self, node, parent, sibling):
        """Mirror of left case 2"""
        sibling.colored = parent.colored
        parent.colored = True
        sibling.left.colored = True
        self.__rotate_right__(parent)

    def __fixup_left_3__(self, node, parent, sibling):
        """
            ?                  ?
          /   \\              /   \\
        node   b    =>     node   b    =>
             /   \\                  \\
            r     b                  r
                                      \\
                                       b

        Solution: convert to case 2 by rotating sibling to right and swapping color between niece and sibling
        """
        sibling.colored = False
        sibling.left.colored = True
        self.__rotate_right__(sibling)
        self.__remove_fixup__(node)

    def __fixup_right_3__(self, node, parent, sibling):
        """Mirror of left case 3"""
        sibling.colored = False
        sibling.right.colored = True
        self.__rotate_left__(sibling)
        self.__remove_fixup__(node)

    def __fixup_right_4__(self, node, parent, sibling):
        """
            ?              ?
          /   \\          /   \\
        node   b    => node   r
             /   \\          /   \\
            b     b        b     b
        Color sibling red and continue from parent
        """
        sibling.colored = False
        self.__remove_fixup__(parent)

    def __fixup_left_4__(self, node, parent, sibling):
        """
            ?              ?
          /   \\          /   \\
        node   b    => node   r
             /   \\          /   \\
            b     b        b     b
        Color sibling red and continue from parent
        """
        sibling.colored = False
        self.__remove_fixup__(parent)

    def __remove_fixup__(self, node):
        if node == self.root:
            return
        if not node.colored:
            node.colored = True
            return

        parent = node.parent
        if parent.left == node:
            dir = self.left_idx
            sibling = parent.right
            niece, nephew = sibling.left, sibling.right
        else:
            dir = self.right_idx
            sibling = parent.left
            niece, nephew = sibling.right, sibling.left

        if not sibling.colored:
            self.fixups[dir][0](node, parent, sibling)
        elif nephew and not nephew.colored:
            self.fixups[dir][1](node, parent, sibling)
        elif niece and not niece.colored:
            self.fixups[dir][2](node, parent, sibling)
        else:
            self.fixups[dir][3](node, parent, sibling)


class RBTree(BSTree, RBTreeRebalance, RBTreeFixup):
    def __init__(self, initializer: dict | list | None = None):
        """

        Function:

        - Initialize a Red-Black Tree, optionally with an initializer.

        Optional Parameters:

        - initializer: A dictionary or list to initialize the tree with.
            - What: A dict with key-value pairs or a list of keys/tuples.
            - Why: To populate the tree with initial data.
            - Default: None
            - Example:
                - dict: {key1: value1, key2: value2}
                - list: [key1, key2] or [(key1, value1), (key2, value2)]
            - Note: All keys should be comparable in order to maintain the tree properties.
                - Example: All keys are integers or strings.
                - Invalid Example: Mixing integers and strings as keys.
                - Custom objects used as keys should implement comparison methods.
        """
        super().__init__()
        self.left_idx = 0  # Left Index for rotations and fixups
        self.right_idx = 1  # Right Index for rotations and fixups
        self.rotations = [
            [self.__rebalance_ll__, self.__rebalance_lr__],
            [self.__rebalance_rl__, self.__rebalance_rr__],
        ]

        self.fixups = [
            [
                self.__fixup_left_1__,
                self.__fixup_left_2__,
                self.__fixup_left_3__,
                self.__fixup_left_4__,
            ],
            [
                self.__fixup_right_1__,
                self.__fixup_right_2__,
                self.__fixup_right_3__,
                self.__fixup_right_4__,
            ],
        ]

        if initializer:
            if type(initializer) == dict:
                for k, v in initializer.items():
                    self.insert(k, v)
            else:
                for k in initializer:
                    if type(k) is tuple:
                        self.insert(key=k[0], value=k[1])
                    else:
                        self.insert(key=k)

    def insert(self, key: any, value: any = None) -> RBNode:
        """
        Function:

        - Insert a key-value pair into the Red-Black Tree.
        - If a node with the same key already exists, its value is updated.

        Required Parameters:

        - key: The key to insert into the tree.
            - What: Any data type that supports comparison operations.
            - Why: Used to maintain the binary search tree property.
            - Example: An integer, string, or custom object with comparison methods.

        Optional Parameters:

        - value: The value associated with the key.
            - What: Any data type.
            - Why: Stores the data or information related to the key.
            - Default: None
        """
        node = RBNode(key, value, False if self.root else True)
        if self.__insert_node__(self.root, node):
            self.__rebalance__(node)

    def remove(self, key: any) -> None:
        """
        Function:

        - Remove a node with the specified key from the Red-Black Tree.
        - Note: If the key is not found, the tree remains unchanged.

        Required Parameters:

        - key: The key of the node to remove from the tree.
            - What: Any data type that supports comparison operations.
            - Why: Used to locate the node to be removed.
            - Example: An integer, string, or custom object with comparison methods.

        """
        if not self.root:
            return

        leaf = node = self.find(key)
        if node == None:
            return

        # Swap node to delete key & value at leaf
        while leaf:
            if node.left:
                leaf = self.get_max(node.left)
            elif node.right:
                leaf = self.get_min(node.right)
            else:
                break

            node.key, leaf.key = leaf.key, node.key
            node.val, leaf.val = leaf.val, node.val
            node = leaf

        # Fixup RBTree
        self.__remove_fixup__(leaf)

        # Remove leaf
        if leaf == self.root:
            self.root = None
        else:
            parent = leaf.parent
            if parent.left == leaf:
                leaf.parent.left = None
            else:
                leaf.parent.right = None
            leaf.parent = None
