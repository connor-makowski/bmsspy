# General Imports
from decimal import Decimal

# Local Imports
from bmsspy.helpers.utils import convert_to_constant_degree, convert_to_constant_out_degree, convert_from_constant_degree


print("\n===============\nConstant Degree Tests:\n===============")

graph = [
    {1: 1, 2: 1, 3: 1},
    {2: 1, 3: 1},
    {3: 1},
    {0: 1},
]

graph = [
    {k: Decimal(v) for k, v in i.items()} for i in graph
]

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
    'graph': [
        {1: Decimal('1'), 4: Decimal('0')},
        {2: Decimal('1'), 3: Decimal('1')},
        {3: Decimal('1')},
        {0: Decimal('1')},
        {2: Decimal('1'), 5: Decimal('0')},
        {3: Decimal('1'), 0: Decimal('0')}
    ],
    'idx_map': [0, 1, 2, 3, 0, 0],
    'original_graph_len': 4
}

converted_out_3 = convert_to_constant_out_degree(graph, out_degree=3)
expected_out_3 = {
    'graph': graph,
    'idx_map': [0, 1, 2, 3],
    'original_graph_len': 4
}

failed = False
if converted == expected and converted_out == expected_out and converted_out_3 == expected_out_3:
    pass
else:
    failed = True


if not failed:
    print("Constant Degree Conversion Test: PASS")
else:
    print("Constant Degree Conversion Test: FAIL")
