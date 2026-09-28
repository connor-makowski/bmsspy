from decimal import Decimal
from bmsspy.helpers.utils import (
    convert_to_constant_degree,
    convert_to_constant_out_degree,
)


def test_constant_degree():
    graph = [
        {1: 1, 2: 1, 3: 1},
        {2: 1, 3: 1},
        {3: 1},
        {0: 1},
    ]
    graph = [{k: Decimal(v) for k, v in i.items()} for i in graph]
    converted = convert_to_constant_degree(graph)

    expected = {
        "graph": [
            {1: Decimal("1"), 4: Decimal("0")},
            {2: Decimal("1"), 3: Decimal("1")},
            {6: Decimal("1")},
            {0: Decimal("1"), 6: Decimal("0")},
            {2: Decimal("1"), 5: Decimal("0")},
            {0: Decimal("0"), 7: Decimal("1")},
            {7: Decimal("0")},
            {3: Decimal("0")},
        ],
        "idx_map": [0, 1, 2, 3, 0, 0, 3, 3],
        "original_graph_len": 4,
    }

    converted_out = convert_to_constant_out_degree(graph, out_degree=2)
    expected_out = {
        "graph": [
            {1: Decimal("1"), 4: Decimal("0")},
            {2: Decimal("1"), 3: Decimal("1")},
            {3: Decimal("1")},
            {0: Decimal("1")},
            {2: Decimal("1"), 5: Decimal("0")},
            {3: Decimal("1"), 0: Decimal("0")},
        ],
        "idx_map": [0, 1, 2, 3, 0, 0],
        "original_graph_len": 4,
    }

    converted_out_3 = convert_to_constant_out_degree(graph, out_degree=3)
    expected_out_3 = {
        "graph": graph,
        "idx_map": [0, 1, 2, 3],
        "original_graph_len": 4,
    }

    assert converted == expected
    assert converted_out == expected_out
    assert converted_out_3 == expected_out_3

    # C++ implementation checks
    from bmsspy import has_cpp

    if has_cpp():
        from bmsspy._cpp import (
            convert_to_constant_degree as cpp_convert_to_constant_degree,
            convert_to_constant_out_degree as cpp_convert_to_constant_out_degree,
        )

        raw_graph = [
            {1: 1.0, 2: 1.0, 3: 1.0},
            {2: 1.0, 3: 1.0},
            {3: 1.0},
            {0: 1.0},
        ]
        cpp_cd = cpp_convert_to_constant_degree(raw_graph)
        cpp_cd_out = cpp_convert_to_constant_out_degree(raw_graph, 2)

        expected_cpp_graph = [
            {k: float(v) for k, v in d.items()} for d in expected["graph"]
        ]
        expected_cpp_out_graph = [
            {k: float(v) for k, v in d.items()} for d in expected_out["graph"]
        ]

        assert cpp_cd["graph"] == expected_cpp_graph
        assert cpp_cd["idx_map"] == expected["idx_map"]
        assert cpp_cd["original_graph_len"] == expected["original_graph_len"]

        assert cpp_cd_out["graph"] == expected_cpp_out_graph
        assert cpp_cd_out["idx_map"] == expected_out["idx_map"]
        assert (
            cpp_cd_out["original_graph_len"]
            == expected_out["original_graph_len"]
        )


if __name__ == "__main__":
    print("\n===============\nConstant Degree Tests:\n===============")
    try:
        test_constant_degree()
        print("Constant Degree Conversion Test: PASS")
    except AssertionError:
        print("Constant Degree Conversion Test: FAIL")
