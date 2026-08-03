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


if __name__ == "__main__":
    print("\n===============\nConstant Degree Tests:\n===============")
    try:
        test_constant_degree()
        print("Constant Degree Conversion Test: PASS")
    except AssertionError:
        print("Constant Degree Conversion Test: FAIL")
