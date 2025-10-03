#ifndef BMSSP_DATA_STRUCTURE_H
#define BMSSP_DATA_STRUCTURE_H

#include <limits>
#include <list>
#include <set>
#include <unordered_map>
#include <vector>
#include <memory>
#include <stdexcept>
#include <string>
#include <sstream>
#include <unordered_set>
#include "rbtree.cpp"
#include "quicksplit.hpp"

using namespace std;

constexpr double INF = numeric_limits<double>::infinity();

struct LinkedListNode {
    int key;
    double value;
    weak_ptr<class LinkedList> parent_list;
    shared_ptr<LinkedListNode> next;
    weak_ptr<LinkedListNode> prev;

    LinkedListNode(int k = 0, double v = INF, shared_ptr<class LinkedList> parent = nullptr);

    string to_string() const;
};

struct LinkedList : enable_shared_from_this<LinkedList> {
    shared_ptr<LinkedListNode> head;
    shared_ptr<LinkedListNode> tail;
    size_t size;
    double upper_bound;
    weak_ptr<LinkedList> prev_list;
    shared_ptr<LinkedList> next_list;

    LinkedList();

    struct iterator {
        shared_ptr<LinkedListNode> current;

        iterator(shared_ptr<LinkedListNode> start);

        iterator& operator++();
        bool operator!=(const iterator& other) const;
        bool operator==(const iterator& other) const;
        shared_ptr<LinkedListNode> operator*() const;
    };

    iterator begin() const;
    iterator end() const;

    void append(int key, double value);
    void remove(shared_ptr<LinkedListNode> node);
    bool is_empty() const;
    string to_string() const;
};

class BmsspDataStructure {
public:
    int subset_size;
    int pull_size;
    double upper_bound;

    unordered_map<int, pair<shared_ptr<LinkedListNode>, int>> keys;
    shared_ptr<LinkedList> D0;
    RBTree<double, shared_ptr<LinkedList>> D1;

    BmsspDataStructure(int subset_size_, double upper_bound_);

    void delete_d1(int key);
    void delete_d0(int key);
    void insert_key_value(int key, double value);
    void split(shared_ptr<LinkedList> linked_list);
    void batch_prepend(const std::set<std::pair<int, double>>& key_value_pairs);
    pair<double, unordered_set<int>> pull();
    bool is_empty() const;
};

#endif // BMSSP_DATA_STRUCTURE_H