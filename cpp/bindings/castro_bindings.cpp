#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/pair.h>
#include <nanobind/stl/unordered_map.h>
#include <nanobind/stl/variant.h>
#include "../src/castro.hpp"

namespace nb = nanobind;

NB_MODULE(castro_cpp, m) {
    m.doc() = "Python bindings for CASTRO's implementation of BMSSP (Batch Multiple-Source Shortest Paths)";
    
    // Bind the bmssp class template for different weight types
    // Using double as the weight type

    // Bind the result struct for double
    nb::class_<spp::BMSSPResult<double>>(m, "BMSSPResult")
        .def_ro("origin_id", &spp::BMSSPResult<double>::origin_id)
        .def_ro("distance_matrix", &spp::BMSSPResult<double>::distance_matrix)
        .def_ro("predecessors", &spp::BMSSPResult<double>::predecessors);

    nb::class_<spp::bmssp<double>>(m, "BMSSP")
        .def(nb::init<const std::vector<std::vector<std::pair<int, double>>>&>(),
             nb::arg("adj"),
             "Initialize BMSSP with adjacency list")
        .def("solve", &spp::bmssp<double>::solve,
             nb::arg("s"),
             "Solve SSSP from source vertex s, returns a dictionary with origin_id, distance_matrix, and predecessors");

    // Bind the result struct for int
    nb::class_<spp::BMSSPResult<int>>(m, "BMSSPResult_Int")
        .def_ro("origin_id", &spp::BMSSPResult<int>::origin_id)
        .def_ro("distance_matrix", &spp::BMSSPResult<int>::distance_matrix)
        .def_ro("predecessors", &spp::BMSSPResult<int>::predecessors);
    
    // Also bind for integer weights if needed
    nb::class_<spp::bmssp<int>>(m, "BMSSP_Int")
        .def(nb::init<const std::vector<std::vector<std::pair<int, int>>>&>(),
             nb::arg("adj"),
             "Initialize BMSSP with adjacency list")
        .def("solve", &spp::bmssp<int>::solve,
             nb::arg("s"),
             "Solve SSSP from source vertex s, returns vector of distances");
}