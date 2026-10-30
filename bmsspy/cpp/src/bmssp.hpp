#pragma once

#include <vector>
#include <optional>
#include <string>
#include <cmath>
#include <stdexcept>
#include "utils.hpp"
#include "bmssp_core.hpp"

namespace bmsspy {

struct BmsspSolveResult {
    std::vector<int> origin_id;
    std::optional<int> destination_id;
    std::vector<int> predecessor;
    std::vector<double> distance_matrix;
    std::optional<std::vector<int>> path;
    std::optional<double> length;
};

class CppBmssp {
public:
    AdjGraph original_graph;
    int precision;
    bool use_constant_degree_graph;
    std::string constant_degree_mode;

    ConstantDegreeResult cd_info;
    AdjGraph used_graph;
    AdjGraphWithAdj edge_adj_graph;
    dist_t counter_value;
    dist_t weight_multiplier;

    CppBmssp(
        const AdjGraph& graph,
        int prec = 6,
        bool use_cd = true,
        const std::string& cd_mode = "degree"
    );

    BmsspSolveResult solve(
        const std::vector<int>& origin_ids,
        std::optional<int> destination_id = std::nullopt,
        int pivot_relaxation_steps = -1,
        int target_tree_depth = -1
    );
};

} // namespace bmsspy

