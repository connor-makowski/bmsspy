# General Imports
from decimal import Decimal

# Local Imports
from bmsspy.helpers.utils import convert_to_constant_degree

graph = [
    {1: 1, 2: 1, 3: 1},
    {2: 1, 3: 1},
    {3: 1},
    {0: 1},
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


if converted == expected:
    print("Constant Degree Conversion Test: PASS")
else:
    print("Constant Degree Conversion Test: FAIL")
