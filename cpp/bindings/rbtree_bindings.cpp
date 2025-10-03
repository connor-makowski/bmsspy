#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "../src/rbtree.cpp"

namespace py = pybind11;

// Helper function to bind RBTree for a specific type combination
template<typename K, typename V>
void bind_rbtree(py::module& m, const std::string& type_name) {
    std::string class_name = "RBTree_" + type_name;
    
    py::class_<BSNode<K, V>>(m, (std::string("BSNode_") + type_name).c_str())
        .def_readonly("key", &BSNode<K, V>::key)
        .def_readonly("val", &BSNode<K, V>::val)
        .def_readonly("parent", &BSNode<K, V>::parent)
        .def_readonly("left", &BSNode<K, V>::left)
        .def_readonly("right", &BSNode<K, V>::right)
        .def("num_nodes", &BSNode<K, V>::num_nodes);

    py::class_<RBTree<K, V>>(m, class_name.c_str())
        .def(py::init<>())
        .def(py::init<std::initializer_list<std::pair<const K, V>>>())
        .def(py::init<std::initializer_list<K>>())
        .def(py::init<const std::map<K, V>&>())
        .def(py::init<const std::vector<K>&>())
        .def(py::init<const std::vector<std::pair<K, V>>&>())
        
        .def("insert", &RBTree<K, V>::insert, 
             py::arg("key"), py::arg("value") = V(),
             "Insert a key-value pair into the tree")
        
        .def("remove", &RBTree<K, V>::remove,
             py::arg("key"),
             "Remove a node with the specified key")
        
        .def("find", &RBTree<K, V>::find,
             py::arg("key"), py::arg("target") = "exact",
             py::return_value_policy::reference,
             "Find a node by key (target: 'exact', 'upper', or 'lower')")
        
        .def("get", &RBTree<K, V>::get,
             py::arg("key"), py::arg("default_val") = V(),
             "Get value by key with optional default")
        
        .def("__getitem__", &RBTree<K, V>::operator[],
             py::arg("key"),
             "Get value by key (dictionary-like access)")
        
        .def("__len__", &RBTree<K, V>::size,
             "Get the number of nodes in the tree")
        
        .def("size", &RBTree<K, V>::size,
             "Get the number of nodes in the tree")
        
        .def("empty", &RBTree<K, V>::empty,
             "Check if tree is empty")
        
        .def("get_max", &RBTree<K, V>::get_max,
             py::arg("node"),
             py::return_value_policy::reference,
             "Get maximum node in subtree")
        
        .def("get_min", &RBTree<K, V>::get_min,
             py::arg("node"),
             py::return_value_policy::reference,
             "Get minimum node in subtree");
}

PYBIND11_MODULE(rbtree_cpp, m) {
    m.doc() = "Red-Black Tree algorithms module";

    // Bind RBTree for common type combinations
    bind_rbtree<int, int>(m, "int_int");
    bind_rbtree<int, std::string>(m, "int_str");
    bind_rbtree<std::string, int>(m, "str_int");
    bind_rbtree<std::string, std::string>(m, "str_str");
    bind_rbtree<double, double>(m, "double_double");
    bind_rbtree<int, double>(m, "int_double");
    bind_rbtree<double, int>(m, "double_int");
    bind_rbtree<double, std::string>(m, "double_str");
    bind_rbtree<std::string, double>(m, "str_double");
}