#pragma once

#include <vector>
#include <queue>
#include <cmath>
#include <limits>
#include <algorithm>
#include <utility>
#include <stdexcept>
#include <iostream>
#include "fast.hpp"
#include "data_structure.hpp"
#include "utils.hpp"

namespace bmsspy {

struct EdgeWithAdj {
    int target;
    dist_t weight;
    dist_t adj;
};

using AdjGraphWithAdj = std::vector<std::vector<EdgeWithAdj>>;

class BmsspCore {
public:
    AdjGraphWithAdj graph;
    size_t graph_len;
    std::vector<dist_t> counter_and_edge_distance_matrix;
    std::vector<dist_t> counter_distance_matrix;
    std::vector<int> predecessor;

    dist_t counter_value;
    int pivot_relaxation_steps; // k
    int target_tree_depth;      // t
    int max_recursion_depth;    // l

    FastSet is_pivot_seen_set;
    FastSet find_pivots_temp_frontier_set;
    FastSet find_pivots_frontier_set_a;
    FastSet find_pivots_frontier_set_b;
    FastDict<std::vector<int>> find_pivots_forest_dict;
    FastSet find_pivots_has_indegree_set;
    FastSet find_pivots_pivots_set;
    FastSet base_case_new_frontier_set;

    std::vector<FastLookup<std::pair<int, LinkedListNode*>>> recursive_bmssp_data_struct_lookups;
    std::vector<FastSet> recursive_bmssp_new_frontier_sets;
    FastSet recursive_bmssp_intermediate_frontier_set;

    BmsspCore(
        const AdjGraphWithAdj& g,
        const std::vector<int>& origin_ids,
        dist_t c_val,
        int k_steps = -1,
        int t_depth = -1
    ) : graph(g), graph_len(g.size()), counter_value(c_val) {
        if (graph_len < 2) {
            throw std::invalid_argument("Graph must have at least 2 nodes");
        }

        counter_and_edge_distance_matrix.assign(graph_len, INF_VAL);
        counter_distance_matrix.assign(graph_len, INF_VAL);
        predecessor.assign(graph_len, -1);

        for (int o : origin_ids) {
            if (o >= 0 && static_cast<size_t>(o) < graph_len) {
                counter_and_edge_distance_matrix[o] = 0.0L;
                counter_distance_matrix[o] = 0.0L;
            }
        }

        double log2_n = std::log2(static_cast<double>(graph_len));
        if (k_steps > 0) {
            pivot_relaxation_steps = k_steps;
        } else {
            pivot_relaxation_steps = std::max(1, static_cast<int>(std::floor(std::pow(log2_n, 1.0 / 3.0))));
        }

        if (t_depth > 0) {
            target_tree_depth = t_depth;
        } else {
            target_tree_depth = std::max(1, static_cast<int>(std::floor(std::pow(log2_n, 2.0 / 3.0))));
        }

        max_recursion_depth = static_cast<int>(std::ceil(log2_n / static_cast<double>(target_tree_depth)));

        is_pivot_seen_set.init(graph_len);
        find_pivots_temp_frontier_set.init(graph_len);
        find_pivots_frontier_set_a.init(graph_len);
        find_pivots_frontier_set_b.init(graph_len);
        find_pivots_forest_dict.init(graph_len);
        find_pivots_has_indegree_set.init(graph_len);
        find_pivots_pivots_set.init(graph_len);
        base_case_new_frontier_set.init(graph_len);

        recursive_bmssp_data_struct_lookups.resize(max_recursion_depth);
        recursive_bmssp_new_frontier_sets.resize(max_recursion_depth);
        for (int d = 0; d < max_recursion_depth; ++d) {
            recursive_bmssp_data_struct_lookups[d].init(graph_len);
            recursive_bmssp_new_frontier_sets[d].init(graph_len);
        }
        recursive_bmssp_intermediate_frontier_set.init(graph_len);

        // Run solver
        recursive_bmssp(max_recursion_depth, INF_VAL, origin_ids);
    }

    bool is_pivot(int root, const FastDict<std::vector<int>>& forest, int threshold) {
        is_pivot_seen_set.clear();
        std::vector<int> stack;
        stack.push_back(root);
        int cnt = 0;

        while (!stack.empty()) {
            int x = stack.back();
            stack.pop_back();

            if (is_pivot_seen_set.contains(x)) continue;
            ++cnt;
            if (cnt >= threshold) return true;

            is_pivot_seen_set.add(x);
            std::vector<int> children;
            if (forest.get(x, children)) {
                stack.insert(stack.end(), children.begin(), children.end());
            }
        }
        return false;
    }

    std::pair<std::vector<int>, std::vector<int>> find_pivots(
        dist_t upper_bound,
        const std::vector<int>& frontier
    ) {
        find_pivots_temp_frontier_set.clear();
        find_pivots_temp_frontier_set.extend(frontier);

        FastSet* prev_frontier = &find_pivots_frontier_set_a;
        FastSet* curr_frontier = &find_pivots_frontier_set_b;
        prev_frontier->clear();
        prev_frontier->extend(frontier);

        for (int step = 0; step < pivot_relaxation_steps; ++step) {
            curr_frontier->clear();
            for (int prev_idx : *prev_frontier) {
                dist_t prev_dist = counter_distance_matrix[prev_idx];
                for (const auto& edge : graph[prev_idx]) {
                    int conn_idx = edge.target;
                    dist_t conn_dist = edge.weight;
                    dist_t edge_adj = edge.adj;

                    dist_t new_dist = prev_dist + conn_dist + counter_value + edge_adj;
                    if (new_dist <= counter_and_edge_distance_matrix[conn_idx]) {
                        if (new_dist < counter_and_edge_distance_matrix[conn_idx]) {
                            predecessor[conn_idx] = prev_idx;
                            counter_and_edge_distance_matrix[conn_idx] = new_dist;
                            counter_distance_matrix[conn_idx] = prev_dist + conn_dist + counter_value;
                        }
                        if (new_dist < upper_bound) {
                            curr_frontier->add(conn_idx);
                        }
                    }
                }
            }
            find_pivots_temp_frontier_set.update(*curr_frontier);
            std::swap(prev_frontier, curr_frontier);

            if (find_pivots_temp_frontier_set.len() > static_cast<size_t>(pivot_relaxation_steps) * frontier.size()) {
                return {frontier, find_pivots_temp_frontier_set.data};
            }
        }

        find_pivots_forest_dict.clear();
        find_pivots_has_indegree_set.clear();

        for (int f_idx : find_pivots_temp_frontier_set) {
            for (const auto& edge : graph[f_idx]) {
                int conn_idx = edge.target;
                if (predecessor[conn_idx] == f_idx) {
                    if (find_pivots_temp_frontier_set.contains(conn_idx)) {
                        find_pivots_forest_dict[f_idx].push_back(conn_idx);
                        find_pivots_has_indegree_set.add(conn_idx);
                    }
                }
            }
        }

        find_pivots_pivots_set.clear();
        for (int f_idx : frontier) {
            if (!find_pivots_has_indegree_set.contains(f_idx)) {
                if (is_pivot(f_idx, find_pivots_forest_dict, pivot_relaxation_steps)) {
                    find_pivots_pivots_set.add(f_idx);
                }
            }
        }

        return {find_pivots_pivots_set.data, find_pivots_temp_frontier_set.data};
    }

    std::pair<dist_t, std::vector<int>> base_case(
        dist_t upper_bound,
        const std::vector<int>& frontier
    ) {
        if (frontier.empty()) return {upper_bound, {}};
        int first_frontier = frontier[0];

        base_case_new_frontier_set.clear();
        using HeapItem = std::pair<dist_t, int>;
        std::priority_queue<HeapItem, std::vector<HeapItem>, std::greater<HeapItem>> heap;

        heap.push({counter_and_edge_distance_matrix[first_frontier], first_frontier});
        dist_t new_upper_bound = upper_bound;

        while (!heap.empty()) {
            auto [dist, idx] = heap.top();
            heap.pop();

            if (base_case_new_frontier_set.len() >= static_cast<size_t>(pivot_relaxation_steps)) {
                new_upper_bound = dist;
                break;
            }

            base_case_new_frontier_set.add(idx);
            dist_t prev_dist = counter_distance_matrix[idx];

            for (const auto& edge : graph[idx]) {
                int conn_idx = edge.target;
                dist_t conn_dist = edge.weight;
                dist_t edge_adj = edge.adj;

                dist_t new_dist = prev_dist + conn_dist + counter_value + edge_adj;
                if (new_dist <= counter_and_edge_distance_matrix[conn_idx] && new_dist < upper_bound) {
                    if (new_dist < counter_and_edge_distance_matrix[conn_idx]) {
                        predecessor[conn_idx] = idx;
                        counter_and_edge_distance_matrix[conn_idx] = new_dist;
                        counter_distance_matrix[conn_idx] = prev_dist + conn_dist + counter_value;
                    }
                    heap.push({new_dist, conn_idx});
                }
            }
        }

        return {new_upper_bound, base_case_new_frontier_set.data};
    }

    std::pair<dist_t, std::vector<int>> recursive_bmssp(
        int recursion_depth,
        dist_t upper_bound,
        const std::vector<int>& frontier
    ) {
        if (recursion_depth == 0) {
            auto res = base_case(upper_bound, frontier);
            return res;
        }

        auto [pivots, temp_frontier] = find_pivots(upper_bound, frontier);

        size_t subset_size = size_t(1) << static_cast<size_t>((recursion_depth - 1) * target_tree_depth);
        FastLookup<std::pair<int, LinkedListNode*>>& lookup = recursive_bmssp_data_struct_lookups[recursion_depth - 1];
        lookup.clear();

        ListBmsspDataStructure data_struct(subset_size, upper_bound, &lookup);
        for (int p : pivots) {
            data_struct.insert_key_value(p, counter_and_edge_distance_matrix[p]);
        }

        FastSet& new_frontier = recursive_bmssp_new_frontier_sets[recursion_depth - 1];
        new_frontier.clear();

        dist_t completion_bound = upper_bound;
        for (int p : pivots) {
            completion_bound = std::min(completion_bound, counter_and_edge_distance_matrix[p]);
        }

        size_t work_budget = static_cast<size_t>(pivot_relaxation_steps) * (size_t(1) << static_cast<size_t>(recursion_depth * target_tree_depth));

        while (new_frontier.len() < work_budget && !data_struct.is_empty()) {
            auto [data_struct_frontier_bound_temp, data_struct_frontier_temp] = data_struct.pull();

            auto [rec_completion_bound, new_frontier_temp] = recursive_bmssp(
                recursion_depth - 1,
                data_struct_frontier_bound_temp,
                data_struct_frontier_temp
            );
            completion_bound = rec_completion_bound;

            new_frontier.update(new_frontier_temp);
            recursive_bmssp_intermediate_frontier_set.clear();

            for (int new_f_idx : new_frontier_temp) {
                dist_t prev_dist = counter_distance_matrix[new_f_idx];
                for (const auto& edge : graph[new_f_idx]) {
                    int conn_idx = edge.target;
                    dist_t conn_dist = edge.weight;
                    dist_t edge_adj = edge.adj;

                    dist_t new_dist = prev_dist + conn_dist + counter_value + edge_adj;
                    if (new_dist <= counter_and_edge_distance_matrix[conn_idx]) {
                        if (new_dist < counter_and_edge_distance_matrix[conn_idx]) {
                            predecessor[conn_idx] = new_f_idx;
                            counter_and_edge_distance_matrix[conn_idx] = new_dist;
                            counter_distance_matrix[conn_idx] = prev_dist + conn_dist + counter_value;
                        }
                        if (data_struct_frontier_bound_temp <= new_dist && new_dist < upper_bound) {
                            data_struct.insert_key_value(conn_idx, new_dist);
                        } else if (completion_bound <= new_dist && new_dist < data_struct_frontier_bound_temp) {
                            recursive_bmssp_intermediate_frontier_set.add(conn_idx);
                        }
                    }
                }
            }

            for (int x : data_struct_frontier_temp) {
                dist_t dist_x = counter_and_edge_distance_matrix[x];
                if (completion_bound <= dist_x && dist_x < data_struct_frontier_bound_temp) {
                    recursive_bmssp_intermediate_frontier_set.add(x);
                }
            }

            std::vector<std::pair<int, dist_t>> to_prepend;
            to_prepend.reserve(recursive_bmssp_intermediate_frontier_set.len());
            for (int x : recursive_bmssp_intermediate_frontier_set) {
                to_prepend.push_back({x, counter_and_edge_distance_matrix[x]});
            }
            data_struct.batch_prepend(std::move(to_prepend));
        }

        completion_bound = std::min(completion_bound, upper_bound);
        for (int v : temp_frontier) {
            if (counter_and_edge_distance_matrix[v] < completion_bound) {
                new_frontier.add(v);
            }
        }

        return {completion_bound, new_frontier.data};
    }
};

} // namespace bmsspy

