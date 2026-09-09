#pragma once

#include <cstddef>
#include <stdexcept>
#include <string>
#include <utility>

namespace bmsspy {

template <typename KeyType, typename ValType>
struct RBNode {
    KeyType key;
    ValType val;
    bool colored; // true = Black, false = Red (following py-redblacktree convention)
    RBNode* parent = nullptr;
    RBNode* left = nullptr;
    RBNode* right = nullptr;

    RBNode(const KeyType& k, const ValType& v, bool c)
        : key(k), val(v), colored(c), parent(nullptr), left(nullptr), right(nullptr) {}

    size_t num_nodes() const {
        size_t count = 1;
        if (left) count += left->num_nodes();
        if (right) count += right->num_nodes();
        return count;
    }
};

template <typename KeyType, typename ValType>
class RBTree {
public:
    using Node = RBNode<KeyType, ValType>;

    Node* root = nullptr;

    RBTree() : root(nullptr) {}

    ~RBTree() {
        clear();
    }

    void clear() {
        destroy_subtree(root);
        root = nullptr;
    }

    size_t size() const {
        return root ? root->num_nodes() : 0;
    }

    bool empty() const {
        return root == nullptr;
    }

    Node* get_min(Node* node) const {
        if (!node) return nullptr;
        while (node->left) {
            node = node->left;
        }
        return node;
    }

    Node* get_max(Node* node) const {
        if (!node) return nullptr;
        while (node->right) {
            node = node->right;
        }
        return node;
    }

    Node* find_fuzzy(Node* node, const KeyType& key) const {
        if (!node) return nullptr;
        if (key < node->key) {
            return node->left ? find_fuzzy(node->left, key) : node;
        } else if (key > node->key) {
            return node->right ? find_fuzzy(node->right, key) : node;
        }
        return node;
    }

    Node* find(const KeyType& key, const std::string& target = "exact") const {
        if (!root) return nullptr;
        Node* node = find_fuzzy(root, key);
        if (!node) return nullptr;

        if (target == "exact") {
            return (node->key == key) ? node : nullptr;
        } else if (target == "upper") {
            if (node->key >= key) return node;
            while (node->parent) {
                node = node->parent;
                if (node->key >= key) return node;
            }
            return nullptr;
        } else if (target == "lower") {
            if (node->key <= key) return node;
            while (node->parent) {
                node = node->parent;
                if (node->key <= key) return node;
            }
            return nullptr;
        }
        throw std::invalid_argument("Invalid target for find in RBTree");
    }

    void insert(const KeyType& key, const ValType& value) {
        Node* node = new Node(key, value, root ? false : true); // Root is Black (true), child is Red (false)
        if (insert_node(root, node)) {
            rebalance(node);
        }
    }

    void remove(const KeyType& key) {
        if (!root) return;

        Node* node = find(key, "exact");
        if (!node) return;

        Node* leaf = node;
        while (leaf) {
            if (node->left) {
                leaf = get_max(node->left);
            } else if (node->right) {
                leaf = get_min(node->right);
            } else {
                break;
            }
            std::swap(node->key, leaf->key);
            std::swap(node->val, leaf->val);
            node = leaf;
        }

        remove_fixup(leaf);

        if (leaf == root) {
            root = nullptr;
        } else {
            Node* parent = leaf->parent;
            if (parent->left == leaf) {
                parent->left = nullptr;
            } else {
                parent->right = nullptr;
            }
        }
        delete leaf;
    }

private:
    void destroy_subtree(Node* node) {
        if (node) {
            destroy_subtree(node->left);
            destroy_subtree(node->right);
            delete node;
        }
    }

    bool insert_node(Node* start, Node* to_insert) {
        if (!root) {
            root = to_insert;
            return true;
        }

        Node* curr = start;
        while (true) {
            if (to_insert->key < curr->key) {
                if (curr->left) {
                    curr = curr->left;
                } else {
                    curr->left = to_insert;
                    to_insert->parent = curr;
                    return true;
                }
            } else if (to_insert->key > curr->key) {
                if (curr->right) {
                    curr = curr->right;
                } else {
                    curr->right = to_insert;
                    to_insert->parent = curr;
                    return true;
                }
            } else {
                curr->val = to_insert->val;
                delete to_insert;
                return false;
            }
        }
    }

    void rotate_right(Node* y) {
        Node* x = y->left;
        Node* T2 = x ? x->right : nullptr;

        if (T2) T2->parent = y;
        y->left = T2;

        if (y == root) {
            root = x;
            if (x) x->parent = nullptr;
        } else {
            Node* T0 = y->parent;
            if (T0->left == y) {
                T0->left = x;
            } else {
                T0->right = x;
            }
            if (x) x->parent = T0;
        }

        if (x) x->right = y;
        y->parent = x;
    }

    void rotate_left(Node* x) {
        Node* y = x->right;
        Node* T2 = y ? y->left : nullptr;

        if (T2) T2->parent = x;
        x->right = T2;

        if (x == root) {
            root = y;
            if (y) y->parent = nullptr;
        } else {
            Node* T0 = x->parent;
            if (T0->left == x) {
                T0->left = y;
            } else {
                T0->right = y;
            }
            if (y) y->parent = T0;
        }

        if (y) y->left = x;
        x->parent = y;
    }

    Node* rebalance_ll(Node* gparent, Node* parent) {
        rotate_right(gparent);
        gparent->colored = !gparent->colored;
        parent->colored = !parent->colored;
        return parent;
    }

    Node* rebalance_lr(Node* gparent, Node* parent) {
        Node* node = parent->right;
        rotate_left(parent);
        return rebalance_ll(gparent, node);
    }

    Node* rebalance_rl(Node* gparent, Node* parent) {
        Node* node = parent->left;
        rotate_right(parent);
        return rebalance_rr(gparent, node);
    }

    Node* rebalance_rr(Node* gparent, Node* parent) {
        rotate_left(gparent);
        gparent->colored = !gparent->colored;
        parent->colored = !parent->colored;
        return parent;
    }

    void rebalance(Node* node) {
        Node* parent = node->parent;
        if (!parent || node->colored || parent->colored) {
            return;
        }

        Node* grandparent = parent->parent;
        if (!grandparent) {
            return;
        }

        int dir_parent = (grandparent->left == parent) ? 0 : 1;
        Node* uncle = (dir_parent == 0) ? grandparent->right : grandparent->left;

        if (uncle && !uncle->colored) {
            uncle->colored = parent->colored = true;
            grandparent->colored = (grandparent == root);
            rebalance(grandparent);
        } else {
            int dir_node = (parent->left == node) ? 0 : 1;
            if (dir_parent == 0) {
                if (dir_node == 0) {
                    rebalance(rebalance_ll(grandparent, parent));
                } else {
                    rebalance(rebalance_lr(grandparent, parent));
                }
            } else {
                if (dir_node == 0) {
                    rebalance(rebalance_rl(grandparent, parent));
                } else {
                    rebalance(rebalance_rr(grandparent, parent));
                }
            }
        }
    }

    void fixup_left_1(Node* node, Node* parent, Node* sibling) {
        sibling->colored = true;
        parent->colored = false;
        rotate_left(parent);
        remove_fixup(node);
    }

    void fixup_right_1(Node* node, Node* parent, Node* sibling) {
        sibling->colored = true;
        parent->colored = false;
        rotate_right(parent);
        remove_fixup(node);
    }

    void fixup_left_2(Node* node, Node* parent, Node* sibling) {
        sibling->colored = parent->colored;
        parent->colored = true;
        if (sibling->right) sibling->right->colored = true;
        rotate_left(parent);
    }

    void fixup_right_2(Node* node, Node* parent, Node* sibling) {
        sibling->colored = parent->colored;
        parent->colored = true;
        if (sibling->left) sibling->left->colored = true;
        rotate_right(parent);
    }

    void fixup_left_3(Node* node, Node* parent, Node* sibling) {
        sibling->colored = false;
        if (sibling->left) sibling->left->colored = true;
        rotate_right(sibling);
        remove_fixup(node);
    }

    void fixup_right_3(Node* node, Node* parent, Node* sibling) {
        sibling->colored = false;
        if (sibling->right) sibling->right->colored = true;
        rotate_left(sibling);
        remove_fixup(node);
    }

    void fixup_left_4(Node* node, Node* parent, Node* sibling) {
        sibling->colored = false;
        remove_fixup(parent);
    }

    void fixup_right_4(Node* node, Node* parent, Node* sibling) {
        sibling->colored = false;
        remove_fixup(parent);
    }

    void remove_fixup(Node* node) {
        if (node == root) return;
        if (!node->colored) {
            node->colored = true;
            return;
        }

        Node* parent = node->parent;
        if (!parent) return;

        int dir = (parent->left == node) ? 0 : 1;
        Node* sibling = (dir == 0) ? parent->right : parent->left;
        if (!sibling) return;

        Node* niece = (dir == 0) ? sibling->left : sibling->right;
        Node* nephew = (dir == 0) ? sibling->right : sibling->left;

        if (!sibling->colored) {
            if (dir == 0) fixup_left_1(node, parent, sibling);
            else fixup_right_1(node, parent, sibling);
        } else if (nephew && !nephew->colored) {
            if (dir == 0) fixup_left_2(node, parent, sibling);
            else fixup_right_2(node, parent, sibling);
        } else if (niece && !niece->colored) {
            if (dir == 0) fixup_left_3(node, parent, sibling);
            else fixup_right_3(node, parent, sibling);
        } else {
            if (dir == 0) fixup_left_4(node, parent, sibling);
            else fixup_right_4(node, parent, sibling);
        }
    }
};

} // namespace bmsspy
