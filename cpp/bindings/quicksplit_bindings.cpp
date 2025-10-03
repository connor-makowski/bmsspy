#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/quicksplit.hpp"  // Include header, NOT .cpp

namespace py = pybind11;

PYBIND11_MODULE(quicksplit_cpp, m) {
    py::class_<QuickSplitResult>(m, "QuickSplitResult")
        .def_readonly("lower", &QuickSplitResult::lower)
        .def_readonly("higher", &QuickSplitResult::higher)
        .def_readonly("pivot", &QuickSplitResult::pivot);

    py::class_<QuickSplitDictResult>(m, "QuickSplitDictResult")
        .def_readonly("lower", &QuickSplitDictResult::lower)
        .def_readonly("higher", &QuickSplitDictResult::higher)
        .def_readonly("pivot", &QuickSplitDictResult::pivot);

    m.def("median", &median, py::arg("arr"), py::arg("split") = true);
    m.def("median_of_medians", &median_of_medians, py::arg("arr"), py::arg("split_size") = 5, py::arg("split") = true);
    m.def("quicksplit", &quicksplit, py::arg("arr"), py::arg("lower_bucket_size") = -1);
    m.def("quicksplit_dict", &quicksplit_dict, py::arg("data"), py::arg("lower_bucket_size") = -1);
}