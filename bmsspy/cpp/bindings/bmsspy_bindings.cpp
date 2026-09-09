#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/optional.h>
#include <nanobind/stl/pair.h>
#include "../src/bmssp.hpp"
#include "../src/utils.hpp"
#include "../src/quicksplit.hpp"

namespace nb = nanobind;

namespace bmsspy {

static AdjGraph py_graph_to_cpp(nb::handle py_graph) {
    AdjGraph graph;
    if (!nb::isinstance<nb::list>(py_graph)) {
        throw std::invalid_argument("Graph must be a list of dictionaries");
    }
    nb::list list_obj = nb::borrow<nb::list>(py_graph);
    size_t n = nb::len(list_obj);
    graph.resize(n);

    for (size_t u = 0; u < n; ++u) {
        nb::handle item = list_obj[u];
        if (nb::isinstance<nb::dict>(item)) {
            nb::dict dict_obj = nb::borrow<nb::dict>(item);
            graph[u].reserve(nb::len(dict_obj));
            for (auto [key, val] : dict_obj) {
                int target = nb::cast<int>(key);
                double weight = nb::cast<double>(val);
                graph[u].push_back({target, weight});
            }
        }
    }
    return graph;
}

class PyBmsspWrapper {
public:
    CppBmssp solver;
    bool is_single_origin = true;

    PyBmsspWrapper(nb::handle py_graph, int precision = 6, bool use_cd = true)
        : solver(py_graph_to_cpp(py_graph), precision, use_cd) {}

    nb::dict solve(
        nb::handle origin_id,
        nb::handle destination_id = nb::none(),
        nb::handle pivot_relaxation_steps = nb::none(),
        nb::handle target_tree_depth = nb::none()
    ) {
        std::vector<int> origins;
        bool single_origin = false;

        if (nb::isinstance<nb::int_>(origin_id)) {
            origins.push_back(nb::cast<int>(origin_id));
            single_origin = true;
        } else if (nb::isinstance<nb::set>(origin_id)) {
            nb::set s = nb::borrow<nb::set>(origin_id);
            for (auto item : s) {
                origins.push_back(nb::cast<int>(item));
            }
        } else if (nb::isinstance<nb::list>(origin_id)) {
            nb::list l = nb::borrow<nb::list>(origin_id);
            for (auto item : l) {
                origins.push_back(nb::cast<int>(item));
            }
        } else {
            throw std::invalid_argument("origin_id must be an int, set, or list of ints");
        }

        std::optional<int> dest = std::nullopt;
        if (!destination_id.is_none()) {
            dest = nb::cast<int>(destination_id);
        }

        int k_steps = -1;
        if (!pivot_relaxation_steps.is_none()) {
            k_steps = nb::cast<int>(pivot_relaxation_steps);
        }

        int t_depth = -1;
        if (!target_tree_depth.is_none()) {
            t_depth = nb::cast<int>(target_tree_depth);
        }

        BmsspSolveResult res = solver.solve(origins, dest, k_steps, t_depth);

        nb::dict out;
        if (single_origin) {
            out["origin_id"] = origins[0];
        } else {
            nb::list o_list;
            for (int o : origins) o_list.append(o);
            out["origin_id"] = o_list;
        }

        if (dest.has_value()) {
            out["destination_id"] = dest.value();
        } else {
            out["destination_id"] = nb::none();
        }

        nb::list pred_list;
        for (int p : res.predecessor) pred_list.append(p);
        out["predecessor"] = pred_list;

        nb::list dist_list;
        for (double d : res.distance_matrix) {
            if (d >= INF_VAL) {
                dist_list.append(std::numeric_limits<double>::infinity());
            } else {
                dist_list.append(d);
            }
        }
        out["distance_matrix"] = dist_list;

        if (res.path.has_value()) {
            nb::list path_list;
            for (int node : res.path.value()) path_list.append(node);
            out["path"] = path_list;
        } else {
            out["path"] = nb::none();
        }

        if (res.length.has_value()) {
            out["length"] = res.length.value();
        } else {
            out["length"] = nb::none();
        }

        return out;
    }
};

class PyListBmsspDataStructure {
public:
    FastLookup<std::pair<int, LinkedListNode*>> lookup;
    ListBmsspDataStructure ds;

    PyListBmsspDataStructure(size_t subset_sz, double ub, size_t lookup_sz = 100000)
        : ds(subset_sz, static_cast<dist_t>(ub), &lookup) {
        lookup.init(lookup_sz);
    }

    void insert_key_value(int key, double value) {
        ds.insert_key_value(key, static_cast<dist_t>(value));
    }

    void batch_prepend(nb::handle pairs) {
        std::vector<std::pair<int, dist_t>> vec;
        for (auto item : pairs) {
            auto tup = nb::borrow<nb::tuple>(item);
            vec.push_back({nb::cast<int>(tup[0]), static_cast<dist_t>(nb::cast<double>(tup[1]))});
        }
        ds.batch_prepend(std::move(vec));
    }

    nb::tuple pull() {
        auto [rem, subset] = ds.pull();
        nb::list sub_list;
        for (int k : subset) sub_list.append(k);
        return nb::make_tuple(static_cast<double>(rem), sub_list);
    }

    bool is_empty() const {
        return ds.is_empty();
    }
};

} // namespace bmsspy

NB_MODULE(_cpp, m) {
    m.doc() = "C++ accelerated BMSSP shortest path solver for BMSSPy";

    nb::class_<bmsspy::PyBmsspWrapper> bmssp_cls(m, "BmsspC");
    bmssp_cls
        .def(nb::init<nb::handle, int, bool>(),
             nb::arg("graph"),
             nb::arg("precision") = 6,
             nb::arg("use_constant_degree_graph") = true)
        .def("solve", &bmsspy::PyBmsspWrapper::solve,
             nb::arg("origin_id"),
             nb::arg("destination_id") = nb::none(),
             nb::arg("pivot_relaxation_steps") = nb::none(),
             nb::arg("target_tree_depth") = nb::none());

    m.attr("Bmssp") = bmssp_cls;

    nb::class_<bmsspy::PyListBmsspDataStructure>(m, "ListBmsspDataStructure")
        .def(nb::init<size_t, double, size_t>(),
             nb::arg("subset_size"),
             nb::arg("upper_bound"),
             nb::arg("lookup_size") = 100000)
        .def("insert_key_value", &bmsspy::PyListBmsspDataStructure::insert_key_value, nb::arg("key"), nb::arg("value"))
        .def("batch_prepend", &bmsspy::PyListBmsspDataStructure::batch_prepend, nb::arg("key_value_pairs"))
        .def("pull", &bmsspy::PyListBmsspDataStructure::pull)
        .def("is_empty", &bmsspy::PyListBmsspDataStructure::is_empty);

    // Helper functions
    m.def("reconstruct_path", [](int dest_id, const std::vector<int>& pred) {
        return bmsspy::reconstruct_path(dest_id, pred);
    }, nb::arg("destination_id"), nb::arg("predecessor"));

    m.def("median", [](std::vector<double> arr, bool split) {
        return bmsspy::median<double>(arr, split);
    }, nb::arg("arr"), nb::arg("split") = true);

    m.def("median_of_medians", [](std::vector<double> arr, size_t split_size, bool split) {
        return bmsspy::median_of_medians<double>(arr, split_size, split);
    }, nb::arg("arr"), nb::arg("split_size") = 5, nb::arg("split") = true);
}

