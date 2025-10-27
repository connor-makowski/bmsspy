from bmsspy.helpers.utils import convert_to_constant_degree
from decimal import Decimal

graph = [
    {1:1, 2:1, 3:1},
    {2:1, 3:1},
    {3:1},
    {0:1},
]

converted = convert_to_constant_degree(graph, precision=0)

expected = {'graph': [
        {1: Decimal('1.00101'), 4: Decimal('0.00201')}, 
        {2: Decimal('1.00301'), 3: Decimal('1.00401')}, 
        {6: Decimal('1.00501')}, 
        {0: Decimal('1.00601'), 6: Decimal('0.00701')}, 
        {2: Decimal('1.00801'), 5: Decimal('0.00901')}, 
        {0: Decimal('0.01001'), 7: Decimal('1.01101')}, 
        {7: Decimal('0.01201')}, 
        {3: Decimal('0.01301')}
    ], 
    'idx_map': [0, 1, 2, 3, 0, 0, 3, 3], 
    'original_graph_len': 4, 
    'precision': 0
}


if converted == expected:
    print("Constant Degree Conversion Test: PASS")
else:
    print("Constant Degree Conversion Test: FAIL")


