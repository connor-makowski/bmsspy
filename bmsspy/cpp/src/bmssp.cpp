#include "bmssp.hpp"
#include <cmath>
#include <iostream>

namespace bmsspy {

CppBmssp::CppBmssp(
    const AdjGraph& graph,
    int prec,
    bool use_cd
) : original_graph(graph), precision(prec), use_constant_degree_graph(use_cd) {
    if (use_constant_degree_graph) {
        cd_info = convert_to_constant_out_degree(original_graph, 2);
        used_graph = cd_info.graph;
    } else {
        used_graph = original_graph;
        cd_info.original_graph_len = original_graph.size();
    }

    size_t num_nodes = used_graph.size();
    size_t num_edges = 0;
    for (const auto& neighbors : used_graph) {
        num_edges += neighbors.size();
    }

    double log_nodes = std::ceil(std::log10(static_cast<double>(num_nodes * 2 + 1)));
    double log_edges = std::ceil(std::log10(static_cast<double>(num_edges + 1)));

    auto pow10_neg = [](int exp) -> dist_t {
        dist_t res = 1.0Q;
        for (int i = 0; i < exp; ++i) res /= 10.0Q;
        return res;
    };

    counter_value = pow10_neg(precision + static_cast<int>(log_nodes));
    dist_t edge_id_adjustment_value = pow10_neg(precision + static_cast<int>(log_nodes + log_edges));

    dist_t edge_id_value = 0.0Q;
    edge_adj_graph.resize(num_nodes);
    for (size_t u = 0; u < num_nodes; ++u) {
        edge_adj_graph[u].reserve(used_graph[u].size());
        for (const auto& edge : used_graph[u]) {
            edge_id_value += edge_id_adjustment_value;
            edge_adj_graph[u].push_back({edge.target, static_cast<dist_t>(edge.weight), edge_id_value});
        }
    }
}

BmsspSolveResult CppBmssp::solve(
    const std::vector<int>& origin_ids,
    std::optional<int> destination_id,
    int pivot_relaxation_steps,
    int target_tree_depth
) {
    if (origin_ids.empty()) {
        throw std::invalid_argument("Provided origin_ids must have at least 1 node");
    }

    for (int o : origin_ids) {
        if (o < 0 || static_cast<size_t>(o) >= original_graph.size()) {
            throw std::out_of_range("Origin node (" + std::to_string(o) + ") is not in the graph");
        }
    }

    if (destination_id.has_value()) {
        int d = destination_id.value();
        if (d < 0 || static_cast<size_t>(d) >= original_graph.size()) {
            throw std::out_of_range("Destination node (" + std::to_string(d) + ") is not in the graph");
        }
    }

    BmsspCore solver(
        edge_adj_graph,
        origin_ids,
        counter_value,
        pivot_relaxation_steps,
        target_tree_depth
    );

    if (destination_id.has_value()) {
        int d = destination_id.value();
        if (solver.counter_distance_matrix[d] >= INF_VAL) {
            throw std::runtime_error("Something went wrong, the origin and destination nodes are not connected.");
        }
    }

    std::vector<dist_t> raw_dist_matrix;
    std::vector<int> pred_matrix;

    if (use_constant_degree_graph) {
        auto converted = convert_from_constant_degree<dist_t>(
            solver.counter_distance_matrix,
            solver.predecessor,
            cd_info
        );
        raw_dist_matrix = std::move(converted.first);
        pred_matrix = std::move(converted.second);
    } else {
        raw_dist_matrix = std::move(solver.counter_distance_matrix);
        pred_matrix = std::move(solver.predecessor);
    }

    // Round distances to precision and convert to double
    std::vector<double> dist_matrix(raw_dist_matrix.size());
    double factor = std::pow(10.0, precision);
    for (size_t i = 0; i < raw_dist_matrix.size(); ++i) {
        if (raw_dist_matrix[i] >= INF_VAL) {
            dist_matrix[i] = std::numeric_limits<double>::infinity();
        } else {
            dist_matrix[i] = std::round(static_cast<double>(raw_dist_matrix[i]) * factor) / factor;
        }
    }

    BmsspSolveResult result;
    result.origin_id = origin_ids;
    result.destination_id = destination_id;
    result.predecessor = pred_matrix;
    result.distance_matrix = dist_matrix;

    if (destination_id.has_value()) {
        int d = destination_id.value();
        result.path = reconstruct_path(d, pred_matrix);
        result.length = dist_matrix[d];
    } else {
        result.path = std::nullopt;
        result.length = std::nullopt;
    }

    return result;
}

} // namespace bmsspy

