#include "bmssp_data_structure.hpp"
#include <stdexcept>
#include <sstream>
#include "rbtree.cpp"
#include "quicksplit.hpp"

// LinkedListNode Implementation
LinkedListNode::LinkedListNode(int k, double v, shared_ptr<LinkedList> parent)
    : key(k), value(v), parent_list(parent), next(nullptr), prev() {}

string LinkedListNode::to_string() const {
    return "(" + std::to_string(value) + ")";
}

// LinkedList Implementation
LinkedList::LinkedList() : head(nullptr), tail(nullptr), size(0), upper_bound(INF), prev_list(), next_list(nullptr) {}

LinkedList::iterator::iterator(shared_ptr<LinkedListNode> start) : current(start) {}

LinkedList::iterator& LinkedList::iterator::operator++() {
    if (current) current = current->next;
    return *this;
}

bool LinkedList::iterator::operator!=(const iterator& other) const {
    return current != other.current;
}

bool LinkedList::iterator::operator==(const iterator& other) const {
    return current == other.current;
}

shared_ptr<LinkedListNode> LinkedList::iterator::operator*() const {
    return current;
}

LinkedList::iterator LinkedList::begin() const {
    return iterator(head);
}

LinkedList::iterator LinkedList::end() const {
    return iterator(nullptr);
}

void LinkedList::append(int key, double value) {
    auto new_node = make_shared<LinkedListNode>(key, value, shared_from_this());
    ++size;
    if (!head) {
        head = tail = new_node;
    } else {
        tail->next = new_node;
        new_node->prev = tail;
        tail = new_node;
    }
}

void LinkedList::remove(shared_ptr<LinkedListNode> node) {
    if (node->parent_list.lock().get() != this) {
        throw std::invalid_argument("Node does not belong to this linked list.");
    }
    --size;
    auto prev_node = node->prev.lock();
    auto next_node = node->next;

    if (prev_node) prev_node->next = next_node;
    if (next_node) next_node->prev = prev_node;

    if (node == head) head = next_node;
    if (node == tail) tail = prev_node;
}

bool LinkedList::is_empty() const {
    return size == 0;
}

string LinkedList::to_string() const {
    ostringstream oss;
    for (auto it = begin(); it != end(); ++it) {
        oss << "(" << (*it)->key << "," << (*it)->value << ")->";
    }
    oss << "UB:" << upper_bound;
    if (next_list) {
        oss << "\n" << next_list->to_string();
    }
    return oss.str();
}

// BmsspDataStructure Implementation
BmsspDataStructure::BmsspDataStructure(int subset_size_, double upper_bound_)
    : subset_size(max(2, subset_size_)),
      pull_size(max(1, subset_size_)),
      upper_bound(upper_bound_),
      D0(nullptr),
      D1()
{
    auto list = make_shared<LinkedList>();
    list->upper_bound = upper_bound;
    D1.insert(upper_bound, list);
}

void BmsspDataStructure::delete_d1(int key) {
    auto it = keys.find(key);
    if (it == keys.end()) throw invalid_argument("Key not found in data structure.");
    auto list_node = it->second.first;
    keys.erase(it);
    auto linked_list = list_node->parent_list.lock();
    linked_list->remove(list_node);

    if (linked_list->is_empty() && linked_list->upper_bound != upper_bound) {
        auto block = D1.find(linked_list->upper_bound);
        if (block && block->val == linked_list) {
            if (linked_list->next_list && linked_list->next_list->upper_bound == linked_list->upper_bound) {
                block->val = linked_list->next_list;
            } else {
                D1.remove(block->key);
            }
        }
        if (auto prev_list = linked_list->prev_list.lock()) {
            prev_list->next_list = linked_list->next_list;
        }
        if (linked_list->next_list) {
            linked_list->next_list->prev_list = linked_list->prev_list;
        }
    }
}

void BmsspDataStructure::delete_d0(int key) {
    auto it = keys.find(key);
    if (it == keys.end()) return;
    auto list_node = it->second.first;
    keys.erase(it);
    auto linked_list = list_node->parent_list.lock();
    linked_list->remove(list_node);

    if (linked_list->is_empty()) {
        if (auto prev_list = linked_list->prev_list.lock()) {
            prev_list->next_list = linked_list->next_list;
        }
        if (linked_list->next_list) {
            linked_list->next_list->prev_list = linked_list->prev_list;
        }
        if (linked_list == D0) {
            D0 = linked_list->next_list;
        }
    }
}

void BmsspDataStructure::insert_key_value(int key, double value) {
    auto it = keys.find(key);
    if (it != keys.end()) {
        auto &item = it->second;
        if (item.first->value < value) {
            return;
        } else if (item.second == 0) {
            delete_d0(key);
        } else {
            delete_d1(key);
        }
    }

    auto block = D1.find(value, "upper");
    if (!block) throw runtime_error("No suitable linked list found in D1, incorrect upper bound.");

    auto linked_list = block->val;
    linked_list->append(key, value);
    keys[key] = make_pair(linked_list->tail, 1);

    if (linked_list->size > subset_size) {
        split(linked_list);
    }
}

void BmsspDataStructure::split(shared_ptr<LinkedList> linked_list) {
    vector<double> values;
    for (auto it = linked_list->begin(); it != linked_list->end(); ++it) {
        values.push_back((*it)->value);
    }
    auto split_result = quicksplit(values);
    double median_value = split_result.pivot;

    auto current_head = D1.find(median_value);
    bool existing_lower_head = (current_head != nullptr && median_value != linked_list->upper_bound);

    auto new_list = make_shared<LinkedList>();
    int maximum_size = static_cast<int>(linked_list->size / 2);

    // Move nodes < median_value
    for (auto it = linked_list->begin(); it != linked_list->end();) {
        auto node = *it;
        ++it; // increment before possible removal
        if (node->value < median_value) {
            new_list->append(node->key, node->value);
            keys[node->key] = make_pair(new_list->tail, 1);
            linked_list->remove(node);
        }
    }
    // Move nodes == median_value up to max size
    for (auto it = linked_list->begin(); it != linked_list->end();) {
        if (new_list->size >= maximum_size) break;
        auto node = *it;
        ++it;
        if (node->value == median_value) {
            new_list->append(node->key, node->value);
            keys[node->key] = make_pair(new_list->tail, 1);
            linked_list->remove(node);
        }
    }

    if (new_list->is_empty()) return;

    new_list->upper_bound = median_value;

    if (!existing_lower_head) {
        new_list->next_list = linked_list;
        new_list->prev_list = linked_list->prev_list;
        if (auto prev_list = linked_list->prev_list.lock()) {
            prev_list->next_list = new_list;
        }
        linked_list->prev_list = new_list;
        D1.insert(median_value, new_list);
    } else {
        bool all_median = true;
        for (auto it = new_list->begin(); it != new_list->end(); ++it) {
            if ((*it)->value != median_value) {
                all_median = false;
                break;
            }
        }
        if (all_median) {
            new_list->next_list = current_head->val->next_list;
            new_list->prev_list = current_head->val;
            if (current_head->val->next_list) {
                current_head->val->next_list->prev_list = new_list;
            }
            current_head->val->next_list = new_list;
        } else {
            throw runtime_error("Unexpected condition during split.");
        }
    }

    if (linked_list->is_empty()) {
        throw runtime_error("Linked list should not be empty after split.");
    }
}

void BmsspDataStructure::batch_prepend(const std::set<std::pair<int, double>>& key_value_pairs) {
    std::unordered_map<int, double> min_pairs;

    for (const auto& kv : key_value_pairs) {
        int key = kv.first;
        double value = kv.second;
        auto it = min_pairs.find(key);
        if (it == min_pairs.end() || value < it->second) {
            auto existing = keys.find(key);
            if (existing != keys.end()) {
                auto& item = existing->second;
                if (item.first->value < value) continue;
                else if (item.second == 0) delete_d0(key);
                else delete_d1(key);
            }
            min_pairs[key] = value;
        }
    }
    if (min_pairs.empty()) return;

    if (min_pairs.size() <= subset_size) {
        auto old_head = D0;
        D0 = std::make_shared<LinkedList>();
        D0->next_list = old_head;
        if (old_head) old_head->prev_list = D0;
        for (const auto& [key, value] : min_pairs) {
            D0->append(key, value);
            keys[key] = std::make_pair(D0->tail, 0);
        }
    } else {
        std::vector<std::unordered_map<int, double>> stack;
        stack.push_back(min_pairs);

        while (!stack.empty()) {
            auto current_pairs = stack.back();
            stack.pop_back();

            if (current_pairs.size() <= subset_size) {
                auto old_head = D0;
                D0 = std::make_shared<LinkedList>();
                D0->next_list = old_head;
                if (old_head) old_head->prev_list = D0;
                for (const auto& [key, value] : current_pairs) {
                    D0->append(key, value);
                    keys[key] = std::make_pair(D0->tail, 0);
                }
            } else {
                auto split_items = quicksplit_dict(current_pairs);
                if (!split_items.lower.empty()) stack.push_back(split_items.lower);
                if (!split_items.higher.empty()) stack.push_back(split_items.higher);
            }
        }
    }
}

pair<double, unordered_set<int>> BmsspDataStructure::pull() {
    unordered_set<int> smallest_d0;
    if (D0 && !D0->is_empty()) {
        auto current_list = D0;
        while ((int)smallest_d0.size() < subset_size && current_list) {
            for (auto it = current_list->begin(); it != current_list->end(); ++it) {
                smallest_d0.insert((*it)->key);
            }
            current_list = current_list->next_list;
        }
    }

    unordered_set<int> smallest_d1;
    if (D1.root != nullptr) {
        auto current_list = D1.get_min(D1.root)->val;
        while ((int)smallest_d1.size() < subset_size && current_list) {
            for (auto it = current_list->begin(); it != current_list->end(); ++it) {
                smallest_d1.insert((*it)->key);
            }
            current_list = current_list->next_list;
        }
    }

    vector<int> combined;
    combined.reserve(smallest_d0.size() + smallest_d1.size());
    combined.insert(combined.end(), smallest_d0.begin(), smallest_d0.end());
    combined.insert(combined.end(), smallest_d1.begin(), smallest_d1.end());

    vector<int> subset;
    if ((int)combined.size() > pull_size) {
        std::unordered_map<int, double> combined_values;
        for (int k : combined) {
            combined_values[k] = keys[k].first->value;
        }
        auto split_result = quicksplit_dict(combined_values, pull_size);
        for (auto& [k, v] : split_result.lower) {
            subset.push_back(k);
        }
    } else {
        subset = combined;
    }

    for (int key : subset) {
        auto it = keys.find(key);
        if (it != keys.end()) {
            if (it->second.second == 0) {
                delete_d0(key);
            } else {
                delete_d1(key);
            }
        }
    }

    double remaining_best = upper_bound;
    if (D0 && !D0->is_empty()) {
        for (auto it = D0->begin(); it != D0->end(); ++it) {
            if ((*it)->value < remaining_best) remaining_best = (*it)->value;
        }
    }
    auto smallest_block = D1.get_min(D1.root);
    if (smallest_block && smallest_block->val->size > 0) {
        for (auto it = smallest_block->val->begin(); it != smallest_block->val->end(); ++it) {
            if ((*it)->value < remaining_best) remaining_best = (*it)->value;
        }
    }

    return {remaining_best, unordered_set<int>(subset.begin(), subset.end())};
}

bool BmsspDataStructure::is_empty() const {
    return keys.empty();
}

