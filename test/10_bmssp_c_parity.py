import pytest
from bmsspy import Bmssp, BmsspC, has_cpp
from scgraph import GeoGraph, Graph
from scgraph.utils import hard_round
import random


def validate(realized, expected, precision=6):
    realized_clean = [
        (
            hard_round(precision, float(val))
            if float(val) != float("inf")
            else float("inf")
        )
        for val in realized
    ]
    expected_clean = [
        (
            hard_round(precision, float(val))
            if float(val) != float("inf")
            else float("inf")
        )
        for val in expected
    ]
    assert realized_clean == expected_clean


def test_bmssp_c_tiny():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    graph = [{1: 1}, {}]
    for use_cd in [True, False]:
        py_res = Bmssp(graph, use_constant_degree_graph=use_cd).solve(0)
        c_res = BmsspC(graph, use_constant_degree_graph=use_cd).solve(0)
        assert (
            c_res["distance_matrix"] == py_res["distance_matrix"] == [0.0, 1.0]
        )
        assert c_res["predecessor"] == py_res["predecessor"] == [-1, 0]


def test_bmssp_c_basic():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    graph = [
        {1: 1, 2: 1, 3: 10},
        {2: 1, 3: 3, 1: 10},
        {3: 1, 4: 2},
        {4: 2},
        {},
    ]
    for use_cd in [True, False]:
        py_res = Bmssp(graph, use_constant_degree_graph=use_cd).solve(0)
        c_res = BmsspC(graph, use_constant_degree_graph=use_cd).solve(0)
        validate(c_res["distance_matrix"], py_res["distance_matrix"])
        assert c_res["predecessor"] == py_res["predecessor"]

        # With destination
        py_dest = Bmssp(graph, use_constant_degree_graph=use_cd).solve(
            0, destination_id=3
        )
        c_dest = BmsspC(graph, use_constant_degree_graph=use_cd).solve(
            0, destination_id=3
        )
        assert c_dest["length"] == py_dest["length"] == 2.0
        assert c_dest["path"] == py_dest["path"] == [0, 2, 3]


def test_bmssp_c_multi_origin():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    graph = [
        {1: 1, 2: 1},
        {2: 1, 3: 3},
        {3: 1, 4: 2},
        {4: 2},
        {},
    ]
    origins = {0, 2}
    for use_cd in [True, False]:
        py_res = Bmssp(graph, use_constant_degree_graph=use_cd).solve(
            origin_id=origins
        )
        c_res = BmsspC(graph, use_constant_degree_graph=use_cd).solve(
            origin_id=origins
        )
        validate(c_res["distance_matrix"], py_res["distance_matrix"])
        assert c_res["predecessor"] == py_res["predecessor"]


def test_bmssp_c_zero_weight():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    graph = [
        {1: 0, 2: 0, 3: 0, 4: 0},
        {2: 0, 3: 0},
        {3: 0, 4: 0},
        {4: 0, 0: 0},
        {0: 0, 1: 0},
    ]
    for use_cd in [True, False]:
        py_res = Bmssp(graph, use_constant_degree_graph=use_cd).solve(0)
        c_res = BmsspC(graph, use_constant_degree_graph=use_cd).solve(0)
        validate(c_res["distance_matrix"], py_res["distance_matrix"])


def test_bmssp_c_grid_graphs():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    # Generate random grid graphs
    for seed in [42, 100, 2024]:
        rng = random.Random(seed)
        rows, cols = 6, 6
        n = rows * cols
        graph = [{} for _ in range(n)]
        for r in range(rows):
            for c in range(cols):
                u = r * cols + c
                if c + 1 < cols:
                    v = r * cols + (c + 1)
                    w = round(rng.uniform(1.0, 10.0), 2)
                    graph[u][v] = w
                if r + 1 < rows:
                    v = (r + 1) * cols + c
                    w = round(rng.uniform(1.0, 10.0), 2)
                    graph[u][v] = w

        for use_cd in [True, False]:
            b_py = Bmssp(graph, use_constant_degree_graph=use_cd)
            b_c = BmsspC(graph, use_constant_degree_graph=use_cd)
            dijk = Graph(graph).get_shortest_path_tree(origin_id=0)

            res_py = b_py.solve(0)
            res_c = b_c.solve(0)

            validate(res_c["distance_matrix"], dijk["distance_matrix"][:n])
            validate(res_c["distance_matrix"], res_py["distance_matrix"])


def test_bmssp_c_scgraph_networks():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    marnet = GeoGraph.load_geograph("marnet").graph
    us_freeway = GeoGraph.load_geograph("us_freeway").graph

    for g, name in [(marnet, "marnet"), (us_freeway, "us_freeway")]:
        dijk = Graph(g).get_shortest_path_tree(origin_id=1)
        for use_cd in [False, True]:
            c_solver = BmsspC(graph=g, use_constant_degree_graph=use_cd)
            res_c = c_solver.solve(origin_id=1)
            validate(
                res_c["distance_matrix"], dijk["distance_matrix"][: len(g)]
            )

            # Test point to point path
            res_p2p = c_solver.solve(origin_id=1, destination_id=10)
            assert res_p2p["path"] is not None
            assert res_p2p["length"] is not None


def test_bmssp_c_custom_parameters():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    graph = [
        {1: 2.5, 2: 1.2},
        {2: 1.1, 3: 4.3},
        {3: 2.1, 4: 5.5},
        {4: 1.0},
        {},
    ]
    for use_cd in [True, False]:
        solver = BmsspC(graph, precision=4, use_constant_degree_graph=use_cd)
        res = solver.solve(
            origin_id=0,
            destination_id=4,
            pivot_relaxation_steps=3,
            target_tree_depth=2,
        )
        assert res["length"] is not None
        assert res["path"] == [0, 2, 3, 4]


def test_bmssp_c_helper_bindings():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    from bmsspy.cpp import (
        reconstruct_path,
        median,
        median_of_medians,
        ListBmsspDataStructure,
    )

    # reconstruct_path
    pred = [-1, 0, 1, 2]
    assert reconstruct_path(3, pred) == [0, 1, 2, 3]

    # median
    arr = [5.0, 2.0, 9.0, 1.0, 7.0]
    assert median(arr, split=True) == 5.0
    assert median_of_medians(arr, 5, True) == 5.0

    # ListBmsspDataStructure
    ds = ListBmsspDataStructure(subset_size=2, upper_bound=100.0)
    ds.insert_key_value(1, 10.0)
    ds.insert_key_value(2, 20.0)
    ds.insert_key_value(3, 5.0)
    assert not ds.is_empty()
    rem, sub = ds.pull()
    assert len(sub) == 2
    assert sub == [3, 1]
    assert rem == 20.0


def test_bmssp_c_constant_degree_options():
    if not has_cpp():
        pytest.skip("C++ extension not available")
    graph = [
        {1: 1.0, 2: 2.0, 3: 5.0},
        {2: 1.0, 3: 2.0},
        {3: 1.0},
        {},
    ]
    # Test all variations of constant degree mode options
    modes = [
        True,
        "constant_degree",
        "degree",
        "constant_out_degree",
        "out_degree",
        False,
        None,
    ]
    for mode in modes:
        py_sol = Bmssp(graph, use_constant_degree_graph=mode).solve(0)
        c_sol = BmsspC(graph, use_constant_degree_graph=mode).solve(0)
        validate(c_sol["distance_matrix"], py_sol["distance_matrix"])
        assert c_sol["predecessor"] == py_sol["predecessor"]

    # Invalid mode should raise ValueError / std::invalid_argument
    with pytest.raises(Exception):
        Bmssp(graph, use_constant_degree_graph="invalid_mode")
    with pytest.raises(Exception):
        BmsspC(graph, use_constant_degree_graph="invalid_mode")
