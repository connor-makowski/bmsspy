#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/bmssp_data_structure.hpp"  // Include your C++ header files for the data structure

namespace py = pybind11;

PYBIND11_MODULE(bmssp_data_structure_cpp, m) {
    py::class_<BmsspDataStructure>(m, "BmsspDataStructure")
        .def(py::init<int, double>())
        .def("insert_key_value", &BmsspDataStructure::insert_key_value)
        .def("delete_d0", &BmsspDataStructure::delete_d0)
        .def("delete_d1", &BmsspDataStructure::delete_d1)
        .def("batch_prepend", &BmsspDataStructure::batch_prepend)
        .def("pull", &BmsspDataStructure::pull)
        .def("is_empty", &BmsspDataStructure::is_empty)
        .def_readwrite("subset_size", &BmsspDataStructure::subset_size)
        .def_readwrite("pull_size", &BmsspDataStructure::pull_size)
        .def_readwrite("upper_bound", &BmsspDataStructure::upper_bound);
}