import pytest
from bmsspy import Bmssp, BmsspC, has_cpp

original_graph = [
    {3: 1},
    {5: 0, 8: 1, 7: 2},
    {8: 2, 4: 1},
    {0: 1, 6: 1},
    {5: 1, 2: 1},
    {3: 2, 1: 0, 4: 1, 6: 0},
    {3: 1, 5: 0},
    {1: 2},
    {1: 1, 2: 2, 0: 2},
]

reduced_graph = [
    {3: 1.0},
    {8: 1.0, 5: 0.0},
    {8: 2.0, 5: 2.0},
    {5: 1.0},
    {8: 3.0, 5: 1.0},
    {8: 4.0, 3: 1.0, 1: 0.0},
    {3: 1.0, 5: 0.0},
    {1: 2.0},
    {5: 4.0, 3: 3.0, 1: 1.0},
]


def test_original_graph_default():
    solver = Bmssp(original_graph)
    res = solver.solve(4, 1)
    assert res["length"] == 1.0
    assert res["path"] == [4, 5, 1]


def test_reduced_graph_no_cd():
    solver = Bmssp(reduced_graph, use_constant_degree_graph=False)
    res = solver.solve(4, 1)
    assert res["length"] == 1.0
    assert res["path"] == [4, 5, 1]


def test_reduced_graph_out_degree_cd():
    solver = Bmssp(reduced_graph, use_constant_degree_graph="out_degree")
    res = solver.solve(4, 1)
    assert res["length"] == 1.0
    assert res["path"] == [4, 5, 1]


def test_reduced_graph_default_py():
    solver = Bmssp(reduced_graph)
    res = solver.solve(4, 1)
    assert res["length"] == 1.0
    assert res["path"] == [4, 5, 1]


def test_reduced_graph_default_c():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    solver = BmsspC(reduced_graph)
    res = solver.solve(4, 1)
    assert res["length"] == 1.0
    assert res["path"] == [4, 5, 1]
