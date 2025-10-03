#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/bmssp_data_structure.hpp"  // Include your C++ header files for the data structure

namespace py = pybind11;

PYBIND11_MODULE(bmssp_data_structure_cpp, m) {
    // Bind LinkedListNode class
    py::class_<LinkedListNode>(m, "LinkedListNode")
        .def(py::init<int, double, std::shared_ptr<LinkedList>>())
        .def_readwrite("key", &LinkedListNode::key)
        .def_readwrite("value", &LinkedListNode::value)
        .def_readwrite("next", &LinkedListNode::next)
        .def_readwrite("prev", &LinkedListNode::prev)
        .def("to_string", &LinkedListNode::to_string);

    // Bind LinkedList class
    py::class_<LinkedList, std::shared_ptr<LinkedList>>(m, "LinkedList")
        .def(py::init<>())
        .def("append", &LinkedList::append)
        .def("remove", &LinkedList::remove)
        .def("is_empty", &LinkedList::is_empty)
        .def("to_string", &LinkedList::to_string)
        .def("__iter__", [](const LinkedList &list) {
            return py::make_iterator(list.begin(), list.end());
        }, py::keep_alive<0, 1>());

    // Bind BmsspDataStructure class
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