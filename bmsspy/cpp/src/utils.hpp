#pragma once

#include <vector>
#include <cmath>
#include <limits>
#include <algorithm>
#include <utility>

namespace bmsspy {

struct Edge {
    int target;
    double weight;
};

using AdjGraph = std::vector<std::vector<Edge>>;

struct ConstantDegreeResult {
    AdjGraph graph;
    std::vector<int> idx_map;
    size_t original_graph_len;
};

inline ConstantDegreeResult convert_to_constant_out_degree(const AdjGraph& original_graph, int out_degree = 2) {
    size_t original_graph_len = original_graph.size();
    AdjGraph graph = original_graph;
    std::vector<int> idx_map(graph.size());
    for (size_t i = 0; i < graph.size(); ++i) {
        idx_map[i] = static_cast<int>(i);
    }

    for (size_t node_idx = 0; node_idx < original_graph_len; ++node_idx) {
        size_t num_connections = graph[node_idx].size();
        if (num_connections > static_cast<size_t>(out_degree)) {
            size_t step = static_cast<size_t>(out_degree - 1);
            size_t num_partitions = (num_connections + step - 1) / step;

            std::vector<int> partition_idx_mapping;
            partition_idx_mapping.reserve(num_partitions);
            partition_idx_mapping.push_back(static_cast<int>(node_idx));

            size_t curr_len = graph.size();
            for (size_t p = 1; p < num_partitions; ++p) {
                int new_node_id = static_cast<int>(curr_len + p - 1);
                partition_idx_mapping.push_back(new_node_id);
            }

            graph.resize(curr_len + num_partitions - 1);
            idx_map.resize(curr_len + num_partitions - 1, static_cast<int>(node_idx));

            std::vector<Edge> original_edges = std::move(graph[node_idx]);
            graph[node_idx].clear();

            size_t partition_idx = 0;
            size_t partition_counter = 0;
            for (const auto& edge : original_edges) {
                int target_partition_node = partition_idx_mapping[partition_idx];
                graph[target_partition_node].push_back(edge);
                ++partition_counter;
                if (partition_counter >= step) {
                    partition_counter = 0;
                    ++partition_idx;
                }
            }

            for (size_t item_idx = 0; item_idx < partition_idx_mapping.size(); ++item_idx) {
                int from_idx = partition_idx_mapping[item_idx];
                int to_idx = partition_idx_mapping[(item_idx + 1) % partition_idx_mapping.size()];
                graph[from_idx].push_back({to_idx, 0.0});
            }
        }
    }

    return {graph, idx_map, original_graph_len};
}

template <typename T = double>
inline std::pair<std::vector<T>, std::vector<int>> convert_from_constant_degree(
    const std::vector<T>& distance_matrix,
    const std::vector<int>& predecessor_matrix,
    const ConstantDegreeResult& cd_info
) {
    size_t orig_len = cd_info.original_graph_len;
    std::vector<T> converted_dist(distance_matrix.begin(), distance_matrix.begin() + orig_len);
    std::vector<int> converted_pred;
    converted_pred.reserve(orig_len);

    for (size_t loc_idx = 0; loc_idx < orig_len; ++loc_idx) {
        int node_idx = predecessor_matrix[loc_idx];
        while (true) {
            if (node_idx == -1) {
                converted_pred.push_back(-1);
                break;
            } else {
                int mapped = cd_info.idx_map[node_idx];
                if (static_cast<size_t>(mapped) < orig_len && mapped != static_cast<int>(loc_idx)) {
                    converted_pred.push_back(mapped);
                    break;
                } else {
                    node_idx = predecessor_matrix[node_idx];
                }
            }
        }
    }

    return {converted_dist, converted_pred};
}

inline std::vector<int> reconstruct_path(int destination_id, const std::vector<int>& predecessor) {
    std::vector<int> path;
    int curr = destination_id;
    path.push_back(curr);
    while (curr >= 0 && static_cast<size_t>(curr) < predecessor.size() && predecessor[curr] != -1) {
        curr = predecessor[curr];
        path.push_back(curr);
    }
    std::reverse(path.begin(), path.end());
    return path;
}

} // namespace bmsspy
