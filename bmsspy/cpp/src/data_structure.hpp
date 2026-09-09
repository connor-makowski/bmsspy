#pragma once

#include <vector>
#include <limits>
#include <algorithm>
#include <stdexcept>
#include <utility>
#include "fast.hpp"
#include "rbtree.hpp"
#include "quicksplit.hpp"

namespace bmsspy {

using dist_t = __float128;
constexpr dist_t INF_VAL = __builtin_infq();

struct LinkedList;

struct LinkedListNode {
    int key;
    dist_t value;
    LinkedList* parent_list = nullptr;
    LinkedListNode* next = nullptr;
    LinkedListNode* prev = nullptr;

    LinkedListNode(int k = 0, dist_t v = 0.0L, LinkedList* parent = nullptr)
        : key(k), value(v), parent_list(parent), next(nullptr), prev(nullptr) {}
};

struct LinkedList {
    LinkedListNode* head = nullptr;
    LinkedListNode* tail = nullptr;
    size_t size = 0;
    dist_t upper_bound = INF_VAL;
    LinkedList* prev_list = nullptr;
    LinkedList* next_list = nullptr;

    LinkedList() : head(nullptr), tail(nullptr), size(0), upper_bound(INF_VAL), prev_list(nullptr), next_list(nullptr) {}

    ~LinkedList() {
        LinkedListNode* curr = head;
        while (curr) {
            LinkedListNode* nxt = curr->next;
            delete curr;
            curr = nxt;
        }
    }

    void append(int key, dist_t value) {
        LinkedListNode* node = new LinkedListNode(key, value, this);
        ++size;
        if (!head) {
            head = tail = node;
        } else {
            tail->next = node;
            node->prev = tail;
            tail = node;
        }
    }

    void remove(LinkedListNode* node) {
        if (!node || node->parent_list != this) return;
        --size;
        if (node->prev) {
            node->prev->next = node->next;
        }
        if (node->next) {
            node->next->prev = node->prev;
        }
        if (node == head) {
            head = node->next;
        }
        if (node == tail) {
            tail = node->prev;
        }
        node->prev = nullptr;
        node->next = nullptr;
    }

    inline bool is_empty() const {
        return size == 0;
    }
};

class ListBmsspDataStructure {
public:
    size_t subset_size;
    size_t pull_size;
    dist_t upper_bound;
    FastLookup<std::pair<int, LinkedListNode*>>* keys; // shared per depth
    LinkedList* D0 = nullptr;
    RBTree<dist_t, LinkedList*> D1;
    std::vector<LinkedList*> all_allocated_lists; // for safe cleanup

    ListBmsspDataStructure(
        size_t subset_sz,
        dist_t ub,
        FastLookup<std::pair<int, LinkedListNode*>>* lookup
    ) : upper_bound(ub), keys(lookup) {
        subset_size = std::max(size_t(2), subset_sz);
        pull_size = std::max(size_t(1), subset_sz);
        D0 = new LinkedList();
        all_allocated_lists.push_back(D0);

        LinkedList* init_list = new LinkedList();
        init_list->upper_bound = ub;
        all_allocated_lists.push_back(init_list);
        D1.insert(ub, init_list);
    }

    ~ListBmsspDataStructure() {
        for (LinkedList* lst : all_allocated_lists) {
            delete lst;
        }
    }

    void delete_d1(int key) {
        std::pair<int, LinkedListNode*> item;
        if (!keys->get(key, item)) return;
        keys->invalidate(key);
        LinkedListNode* list_node = item.second;
        if (!list_node) return;
        LinkedList* linked_list = list_node->parent_list;
        linked_list->remove(list_node);
        delete list_node;

        if (linked_list->is_empty() && linked_list->upper_bound != upper_bound) {
            auto* block = D1.find(linked_list->upper_bound, "exact");
            if (block && block->val == linked_list) {
                if (linked_list->next_list && linked_list->next_list->upper_bound == linked_list->upper_bound) {
                    block->val = linked_list->next_list;
                } else {
                    D1.remove(block->key);
                }
            }
            if (linked_list->prev_list) {
                linked_list->prev_list->next_list = linked_list->next_list;
            }
            if (linked_list->next_list) {
                linked_list->next_list->prev_list = linked_list->prev_list;
            }
        }
    }

    void delete_d0(int key) {
        std::pair<int, LinkedListNode*> item;
        if (!keys->get(key, item)) return;
        keys->invalidate(key);
        LinkedListNode* list_node = item.second;
        if (!list_node) return;
        LinkedList* linked_list = list_node->parent_list;
        linked_list->remove(list_node);
        delete list_node;

        if (linked_list->is_empty()) {
            if (linked_list->prev_list) {
                linked_list->prev_list->next_list = linked_list->next_list;
            }
            if (linked_list->next_list) {
                linked_list->next_list->prev_list = linked_list->prev_list;
            }
            if (linked_list == D0) {
                D0 = linked_list->next_list;
            }
        }
    }

    void insert_key_value(int key, dist_t value) {
        std::pair<int, LinkedListNode*> item;
        if (keys->get(key, item)) {
            if (item.second && item.second->value < value) {
                return;
            } else if (item.first == 0) {
                delete_d0(key);
            } else {
                delete_d1(key);
            }
        }

        auto* block = D1.find(value, "upper");
        if (!block) {
            throw std::runtime_error("No suitable linked list found in D1, incorrect upper bound.");
        }
        LinkedList* linked_list = block->val;
        linked_list->append(key, value);
        keys->set(key, {1, linked_list->tail});

        if (linked_list->size > subset_size) {
            split(linked_list);
        }
    }

    void split(LinkedList* linked_list) {
        std::vector<dist_t> vals;
        vals.reserve(linked_list->size);
        LinkedListNode* curr = linked_list->head;
        while (curr) {
            vals.push_back(curr->value);
            curr = curr->next;
        }

        dist_t median_value = quicksplit<dist_t>(vals).pivot;
        LinkedList* new_list = new LinkedList();
        all_allocated_lists.push_back(new_list);

        curr = linked_list->head;
        while (curr) {
            LinkedListNode* nxt = curr->next;
            if (curr->value < median_value) {
                new_list->append(curr->key, curr->value);
                keys->set(curr->key, {1, new_list->tail});
                linked_list->remove(curr);
                delete curr;
            }
            curr = nxt;
        }

        new_list->upper_bound = median_value;
        new_list->next_list = linked_list;
        new_list->prev_list = linked_list->prev_list;
        if (linked_list->prev_list) {
            linked_list->prev_list->next_list = new_list;
        }
        linked_list->prev_list = new_list;
        D1.insert(median_value, new_list);
    }

    void batch_prepend(std::vector<std::pair<int, dist_t>> key_value_pairs) {
        // Filter / deduplicate
        std::vector<std::pair<int, dist_t>> filtered;
        filtered.reserve(key_value_pairs.size());

        for (const auto& kv : key_value_pairs) {
            int key = kv.first;
            dist_t value = kv.second;
            std::pair<int, LinkedListNode*> item;
            if (keys->get(key, item)) {
                if (item.second && item.second->value < value) {
                    continue; // Skip
                } else if (item.first == 0) {
                    delete_d0(key);
                } else {
                    delete_d1(key);
                }
            }
            filtered.push_back(kv);
        }

        if (filtered.empty()) return;

        if (filtered.size() <= subset_size) {
            LinkedList* old_head = D0;
            D0 = new LinkedList();
            all_allocated_lists.push_back(D0);
            D0->next_list = old_head;
            if (old_head) old_head->prev_list = D0;
            for (const auto& kv : filtered) {
                D0->append(kv.first, kv.second);
                keys->set(kv.first, {0, D0->tail});
            }
        } else {
            std::vector<std::vector<std::pair<int, dist_t>>> stack;
            stack.push_back(std::move(filtered));
            while (!stack.empty()) {
                auto current_pairs = std::move(stack.back());
                stack.pop_back();
                if (current_pairs.size() <= subset_size) {
                    LinkedList* old_head = D0;
                    D0 = new LinkedList();
                    all_allocated_lists.push_back(D0);
                    D0->next_list = old_head;
                    if (old_head) old_head->prev_list = D0;
                    for (const auto& kv : current_pairs) {
                        D0->append(kv.first, kv.second);
                        keys->set(kv.first, {0, D0->tail});
                    }
                } else {
                    auto split_items = quicksplit_tuple<int, dist_t>(std::move(current_pairs));
                    if (!split_items.lower.empty()) {
                        stack.push_back(std::move(split_items.lower));
                    }
                    if (!split_items.higher.empty()) {
                        stack.push_back(std::move(split_items.higher));
                    }
                }
            }
        }
    }

    std::pair<dist_t, std::vector<int>> pull() {
        std::vector<int> smallest_d0;
        LinkedList* current_list = D0;
        while (smallest_d0.size() < subset_size && current_list != nullptr) {
            LinkedListNode* curr = current_list->head;
            while (curr) {
                smallest_d0.push_back(curr->key);
                curr = curr->next;
            }
            current_list = current_list->next_list;
        }

        std::vector<int> smallest_d1;
        if (D1.root) {
            auto* min_node = D1.get_min(D1.root);
            if (min_node) {
                current_list = min_node->val;
                while (smallest_d1.size() < subset_size && current_list != nullptr) {
                    LinkedListNode* curr = current_list->head;
                    while (curr) {
                        smallest_d1.push_back(curr->key);
                        curr = curr->next;
                    }
                    current_list = current_list->next_list;
                }
            }
        }

        std::vector<int> combined;
        combined.reserve(smallest_d0.size() + smallest_d1.size());
        combined.insert(combined.end(), smallest_d0.begin(), smallest_d0.end());
        combined.insert(combined.end(), smallest_d1.begin(), smallest_d1.end());

        std::vector<int> subset;
        if (combined.size() > pull_size) {
            std::vector<std::pair<int, dist_t>> combined_pairs;
            combined_pairs.reserve(combined.size());
            for (int k : combined) {
                std::pair<int, LinkedListNode*> item;
                if (keys->get(k, item) && item.second) {
                    combined_pairs.push_back({k, item.second->value});
                }
            }
            auto split_res = quicksplit_tuple<int, dist_t>(std::move(combined_pairs), static_cast<int>(pull_size));
            subset.reserve(split_res.lower.size());
            for (const auto& p : split_res.lower) {
                subset.push_back(p.first);
            }
        } else {
            subset = std::move(combined);
        }

        for (int key : subset) {
            std::pair<int, LinkedListNode*> item;
            if (keys->get(key, item)) {
                if (item.first == 0) {
                    delete_d0(key);
                } else {
                    delete_d1(key);
                }
            }
        }

        dist_t remaining_best = upper_bound;
        if (D0 && !D0->is_empty()) {
            LinkedListNode* curr = D0->head;
            while (curr) {
                if (curr->value < remaining_best) remaining_best = curr->value;
                curr = curr->next;
            }
        }
        if (D1.root) {
            auto* smallest_block = D1.get_min(D1.root);
            if (smallest_block && smallest_block->val && smallest_block->val->size > 0) {
                LinkedListNode* curr = smallest_block->val->head;
                while (curr) {
                    if (curr->value < remaining_best) remaining_best = curr->value;
                    curr = curr->next;
                }
            }
        }

        return {remaining_best, subset};
    }

    bool is_empty() const {
        bool d0_empty = (!D0 || D0->is_empty());
        bool d1_empty = (!D1.root || (D1.root->val && D1.root->val->is_empty() && D1.get_min(D1.root) == D1.root));
        return d0_empty && d1_empty;
    }
};

} // namespace bmsspy
