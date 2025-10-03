#ifndef RBTREE_H
#define RBTREE_H

#include <memory>
#include <stdexcept>
#include <functional>
#include <vector>
#include <map>

// Forward declarations
template<typename K, typename V>
class BSNode;

template<typename K, typename V>
class RBNode;

template<typename K, typename V>
class BSTree;

template<typename K, typename V>
class RBTree;

template<typename K, typename V>
class BSNode {
public:
    K key;
    V val;
    BSNode* parent;
    BSNode* left;
    BSNode* right;

    BSNode(const K& key, const V& value = V())
        : key(key), val(value), parent(nullptr), left(nullptr), right(nullptr) {}

    virtual ~BSNode() {
        // Note: Does not delete children - tree handles deletion
    }

    int num_nodes() const {
        return 1 
            + (left ? left->num_nodes() : 0)
            + (right ? right->num_nodes() : 0);
    }
};

template<typename K, typename V>
class BSTree {
public:
    BSNode<K, V>* root;
    BSNode<K, V>* find_fuzzy(BSNode<K, V>* node, const K& key) const {
        if (key < node->key) {
            return node->left ? find_fuzzy(node->left, key) : node;
        } else if (key > node->key) {
            return node->right ? find_fuzzy(node->right, key) : node;
        }
        return node;
    }

    bool insert_node(BSNode<K, V>* start, BSNode<K, V>* to_insert) {
        if (!root) {
            root = to_insert;
            return true;
        }

        BSNode<K, V>* current = start;
        while (true) {
            if (to_insert->key < current->key) {
                if (current->left) {
                    current = current->left;
                } else {
                    current->left = to_insert;
                    to_insert->parent = current;
                    return true;
                }
            } else if (to_insert->key > current->key) {
                if (current->right) {
                    current = current->right;
                } else {
                    current->right = to_insert;
                    to_insert->parent = current;
                    return true;
                }
            } else {
                current->val = to_insert->val;
                return false;
            }
        }
    }

    void rotate_right(BSNode<K, V>* y) {
        BSNode<K, V>* x = y->left;
        
        // Attach T2 to y
        BSNode<K, V>* T2 = x->right;
        if (T2) {
            T2->parent = y;
        }
        y->left = T2;

        // Attach x to T0
        if (y == root) {
            root = x;
            x->parent = nullptr;
        } else {
            BSNode<K, V>* T0 = y->parent;
            if (T0->left == y) {
                T0->left = x;
            } else {
                T0->right = x;
            }
            x->parent = T0;
        }

        // Attach y to x
        y->parent = x;
        x->right = y;
    }

    void rotate_left(BSNode<K, V>* x) {
        BSNode<K, V>* y = x->right;

        // Attach T2 to x
        BSNode<K, V>* T2 = y->left;
        if (T2) {
            T2->parent = x;
        }
        x->right = T2;

        // Attach T0 to y
        if (x == root) {
            root = y;
            y->parent = nullptr;
        } else {
            BSNode<K, V>* T0 = x->parent;
            if (T0->left == x) {
                T0->left = y;
            } else {
                T0->right = y;
            }
            y->parent = T0;
        }

        // Attach x to y
        x->parent = y;
        y->left = x;
    }

    void delete_tree(BSNode<K, V>* node) {
        if (!node) return;
        delete_tree(node->left);
        delete_tree(node->right);
        delete node;
    }

    BSTree() : root(nullptr) {}

    virtual ~BSTree() {
        delete_tree(root);
    }

    virtual void insert(const K& key, const V& value = V()) {
        throw std::runtime_error("Not implemented");
    }

    virtual void remove(const K& key) {
        throw std::runtime_error("Not implemented");
    }

    BSNode<K, V>* find(const K& key, const std::string& target = "exact") const {
        if (!root) return nullptr;
        
        BSNode<K, V>* node = find_fuzzy(root, key);
        
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
        } else {
            throw std::invalid_argument("Invalid target for find");
        }
    }

    bool empty() const {
        return root == nullptr;
    }

    BSNode<K, V>* get_max(BSNode<K, V>* node) const {
        if (node->right) {
            return get_max(node->right);
        }
        return node;
    }

    BSNode<K, V>* get_min(BSNode<K, V>* node) const {
        if (node->left) {
            return get_min(node->left);
        }
        return node;
    }

    V get(const K& key, const V& default_val = V()) const {
        BSNode<K, V>* node = root ? find(key) : nullptr;
        return node ? node->val : default_val;
    }

    V operator[](const K& key) const {
        return get(key);
    }

    int size() const {
        return root ? root->num_nodes() : 0;
    }
};

// ============================================================================
// RBNode - Red-Black Tree Node
// ============================================================================
template<typename K, typename V>
class RBNode : public BSNode<K, V> {
public:
    bool colored; // true = red, false = black

    RBNode(const K& key, const V& value, bool color)
        : BSNode<K, V>(key, value), colored(color) {}
};

// ============================================================================
// RBTree - Red-Black Tree
// ============================================================================
template<typename K, typename V>
class RBTree : public BSTree<K, V> {
public:
    static const int LEFT_IDX = 0;
    static const int RIGHT_IDX = 1;

    using BSTree<K, V>::root;
    using BSTree<K, V>::insert_node;
    using BSTree<K, V>::rotate_left;
    using BSTree<K, V>::rotate_right;
    using BSTree<K, V>::get_max;
    using BSTree<K, V>::get_min;

    // Rebalancing methods
    RBNode<K, V>* rebalance_ll(RBNode<K, V>* gparent, RBNode<K, V>* parent) {
        rotate_right(gparent);
        gparent->colored = !gparent->colored;
        parent->colored = !parent->colored;
        return parent;
    }

    RBNode<K, V>* rebalance_lr(RBNode<K, V>* gparent, RBNode<K, V>* parent) {
        RBNode<K, V>* node = static_cast<RBNode<K, V>*>(parent->right);
        rotate_left(parent);
        return rebalance_ll(gparent, node);
    }

    RBNode<K, V>* rebalance_rl(RBNode<K, V>* gparent, RBNode<K, V>* parent) {
        RBNode<K, V>* node = static_cast<RBNode<K, V>*>(parent->left);
        rotate_right(parent);
        return rebalance_rr(gparent, node);
    }

    RBNode<K, V>* rebalance_rr(RBNode<K, V>* gparent, RBNode<K, V>* parent) {
        rotate_left(gparent);
        gparent->colored = !gparent->colored;
        parent->colored = !parent->colored;
        return parent;
    }

    void rebalance(RBNode<K, V>* node) {
        RBNode<K, V>* parent = static_cast<RBNode<K, V>*>(node->parent);
        if (!parent || node->colored || parent->colored) {
            return;
        }

        RBNode<K, V>* grandparent = static_cast<RBNode<K, V>*>(parent->parent);
        if (!grandparent) {
            return;
        }

        int dir_parent = (grandparent->left == parent) ? LEFT_IDX : RIGHT_IDX;
        RBNode<K, V>* uncle = static_cast<RBNode<K, V>*>(
            dir_parent == LEFT_IDX ? grandparent->right : grandparent->left
        );

        if (uncle && !uncle->colored) {
            uncle->colored = parent->colored = true;
            grandparent->colored = (grandparent == root);
            rebalance(grandparent);
        } else {
            int dir_node = (parent->left == node) ? LEFT_IDX : RIGHT_IDX;
            
            if (dir_parent == LEFT_IDX && dir_node == LEFT_IDX) {
                rebalance(rebalance_ll(grandparent, parent));
            } else if (dir_parent == LEFT_IDX && dir_node == RIGHT_IDX) {
                rebalance(rebalance_lr(grandparent, parent));
            } else if (dir_parent == RIGHT_IDX && dir_node == LEFT_IDX) {
                rebalance(rebalance_rl(grandparent, parent));
            } else {
                rebalance(rebalance_rr(grandparent, parent));
            }
        }
    }

    // Fixup methods after deletion
    void fixup_left_1(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = true;
        parent->colored = false;
        rotate_left(parent);
        remove_fixup(node);
    }

    void fixup_right_1(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = true;
        parent->colored = false;
        rotate_right(parent);
        remove_fixup(node);
    }

    void fixup_left_2(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = parent->colored;
        parent->colored = true;
        static_cast<RBNode<K, V>*>(sibling->right)->colored = true;
        rotate_left(parent);
    }

    void fixup_right_2(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = parent->colored;
        parent->colored = true;
        static_cast<RBNode<K, V>*>(sibling->left)->colored = true;
        rotate_right(parent);
    }

    void fixup_left_3(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = false;
        static_cast<RBNode<K, V>*>(sibling->left)->colored = true;
        rotate_right(sibling);
        remove_fixup(node);
    }

    void fixup_right_3(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = false;
        static_cast<RBNode<K, V>*>(sibling->right)->colored = true;
        rotate_left(sibling);
        remove_fixup(node);
    }

    void fixup_left_4(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = false;
        remove_fixup(parent);
    }

    void fixup_right_4(RBNode<K, V>* node, RBNode<K, V>* parent, RBNode<K, V>* sibling) {
        sibling->colored = false;
        remove_fixup(parent);
    }

    void remove_fixup(RBNode<K, V>* node) {
        if (node == root) {
            return;
        }
        if (!node->colored) {
            node->colored = true;
            return;
        }

        RBNode<K, V>* parent = static_cast<RBNode<K, V>*>(node->parent);
        RBNode<K, V>* sibling;
        RBNode<K, V>* niece;
        RBNode<K, V>* nephew;
        int dir;

        if (parent->left == node) {
            dir = LEFT_IDX;
            sibling = static_cast<RBNode<K, V>*>(parent->right);
            niece = static_cast<RBNode<K, V>*>(sibling->left);
            nephew = static_cast<RBNode<K, V>*>(sibling->right);
        } else {
            dir = RIGHT_IDX;
            sibling = static_cast<RBNode<K, V>*>(parent->left);
            niece = static_cast<RBNode<K, V>*>(sibling->right);
            nephew = static_cast<RBNode<K, V>*>(sibling->left);
        }

        if (!sibling->colored) {
            if (dir == LEFT_IDX) {
                fixup_left_1(node, parent, sibling);
            } else {
                fixup_right_1(node, parent, sibling);
            }
        } else if (nephew && !nephew->colored) {
            if (dir == LEFT_IDX) {
                fixup_left_2(node, parent, sibling);
            } else {
                fixup_right_2(node, parent, sibling);
            }
        } else if (niece && !niece->colored) {
            if (dir == LEFT_IDX) {
                fixup_left_3(node, parent, sibling);
            } else {
                fixup_right_3(node, parent, sibling);
            }
        } else {
            if (dir == LEFT_IDX) {
                fixup_left_4(node, parent, sibling);
            } else {
                fixup_right_4(node, parent, sibling);
            }
        }
    }

    RBTree() : BSTree<K, V>() {}

    RBTree(std::initializer_list<std::pair<const K, V>> initializer) : BSTree<K, V>() {
        for (const auto& pair : initializer) {
            insert(pair.first, pair.second);
        }
    }

    RBTree(std::initializer_list<K> keys) : BSTree<K, V>() {
        for (const K& key : keys) {
            insert(key);
        }
    }

    explicit RBTree(const std::map<K, V>& map_init) : BSTree<K, V>() {
        for (const auto& pair : map_init) {
            insert(pair.first, pair.second);
        }
    }

    explicit RBTree(const std::vector<std::pair<K, V>>& pairs) : BSTree<K, V>() {
        for (const auto& pair : pairs) {
            insert(pair.first, pair.second);
        }
    }

    explicit RBTree(const std::vector<K>& keys) : BSTree<K, V>() {
        for (const K& key : keys) {
            insert(key);
        }
    }

    void insert(const K& key, const V& value = V()) override {
        RBNode<K, V>* node = new RBNode<K, V>(key, value, root ? false : true);
        if (insert_node(root, node)) {
            rebalance(node);
        } else {
            delete node; // Node was not inserted, key already exists
        }
    }

    void remove(const K& key) override {
        if (!root) return;

        BSNode<K, V>* temp = this->find(key);
        if (!temp) return;

        RBNode<K, V>* node = static_cast<RBNode<K, V>*>(temp);
        RBNode<K, V>* leaf = node;

        // Swap node to delete key & value at leaf
        while (leaf) {
            if (node->left) {
                leaf = static_cast<RBNode<K, V>*>(get_max(node->left));
            } else if (node->right) {
                leaf = static_cast<RBNode<K, V>*>(get_min(node->right));
            } else {
                break;
            }

            std::swap(node->key, leaf->key);
            std::swap(node->val, leaf->val);
            node = leaf;
        }

        // Fixup RBTree
        remove_fixup(leaf);

        // Remove leaf
        if (leaf == root) {
            root = nullptr;
        } else {
            BSNode<K, V>* parent = leaf->parent;
            if (parent->left == leaf) {
                parent->left = nullptr;
            } else {
                parent->right = nullptr;
            }
            leaf->parent = nullptr;
        }
        
        delete leaf;
    }
};

#endif // RBTREE_H