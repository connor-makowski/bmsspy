#pragma once

#include <vector>
#include <stdexcept>
#include <cstddef>
#include <algorithm>

namespace bmsspy {

class FastSet {
public:
    int size;
    int scnt;
    std::vector<int> memb;
    std::vector<int> data;

    FastSet(int n = 0) : size(n), scnt(1), memb(n, 0) {
        data.reserve(std::min(n, 1024));
    }

    void init(int n) {
        size = n;
        scnt = 1;
        memb.assign(n, 0);
        data.clear();
        data.reserve(std::min(n, 1024));
    }

    void clear() {
        ++scnt;
        data.clear();
    }

    inline bool contains(int key) const {
        return (key >= 0 && key < size) ? (memb[key] == scnt) : false;
    }

    inline void add(int key) {
        if (key >= 0 && key < size && memb[key] != scnt) {
            memb[key] = scnt;
            data.push_back(key);
        }
    }

    void extend(const std::vector<int>& items) {
        for (int x : items) {
            add(x);
        }
    }

    void update(const FastSet& other) {
        for (int x : other.data) {
            add(x);
        }
    }

    void update(const std::vector<int>& other) {
        for (int x : other) {
            add(x);
        }
    }

    inline size_t len() const {
        return data.size();
    }

    inline bool empty() const {
        return data.empty();
    }

    auto begin() { return data.begin(); }
    auto end() { return data.end(); }
    auto begin() const { return data.begin(); }
    auto end() const { return data.end(); }
};

template <typename T>
class FastDict {
public:
    int size;
    int scnt;
    std::vector<int> memb;
    std::vector<T> vals;
    std::vector<int> data;

    FastDict(int n = 0) : size(n), scnt(1), memb(n, 0), vals(n) {
        data.reserve(std::min(n, 1024));
    }

    void init(int n) {
        size = n;
        scnt = 1;
        memb.assign(n, 0);
        vals.assign(n, T{});
        data.clear();
        data.reserve(std::min(n, 1024));
    }

    void clear() {
        ++scnt;
        data.clear();
    }

    inline bool contains(int key) const {
        return (key >= 0 && key < size) ? (memb[key] == scnt) : false;
    }

    inline void set(int key, const T& val) {
        if (key >= 0 && key < size) {
            if (memb[key] != scnt) {
                memb[key] = scnt;
                data.push_back(key);
            }
            vals[key] = val;
        }
    }

    inline T& operator[](int key) {
        if (key >= 0 && key < size) {
            if (memb[key] != scnt) {
                memb[key] = scnt;
                data.push_back(key);
                vals[key] = T{};
            }
            return vals[key];
        }
        throw std::out_of_range("FastDict index out of range");
    }

    inline bool get(int key, T& out) const {
        if (key >= 0 && key < size && memb[key] == scnt) {
            out = vals[key];
            return true;
        }
        return false;
    }

    inline T get(int key, const T& default_val) const {
        if (key >= 0 && key < size && memb[key] == scnt) {
            return vals[key];
        }
        return default_val;
    }

    inline size_t len() const {
        return data.size();
    }
};

template <typename T>
class FastLookup {
public:
    int size;
    int scnt;
    std::vector<int> memb;
    std::vector<T> vals;

    FastLookup(int n = 0) : size(n), scnt(1), memb(n, 0), vals(n) {}

    void init(int n) {
        size = n;
        scnt = 1;
        memb.assign(n, 0);
        vals.assign(n, T{});
    }

    void clear() {
        ++scnt;
    }

    inline bool contains(int key) const {
        return (key >= 0 && key < size) ? (memb[key] == scnt) : false;
    }

    inline void set(int key, const T& val) {
        if (key >= 0 && key < size) {
            memb[key] = scnt;
            vals[key] = val;
        }
    }

    inline bool get(int key, T& out) const {
        if (key >= 0 && key < size && memb[key] == scnt) {
            out = vals[key];
            return true;
        }
        return false;
    }

    inline void invalidate(int key) {
        if (key >= 0 && key < size) {
            memb[key] = -1;
        }
    }
};

} // namespace bmsspy
