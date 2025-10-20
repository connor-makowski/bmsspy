from bmsspy.helpers.utils import convert_to_constant_degree

graph = [
    {1:1, 2:1, 3:1},
    {2:1, 3:1},
    {3:1},
    {0:1},
]

converted = convert_to_constant_degree(graph)

expected = {
    'graph': [{1: 1, 4: 0}, {2: 1, 7: 1}, {8: 1}, {6: 1, 7: 0}, {2: 1, 5: 0}, {6: 0, 9: 1}, {0: 0}, {8: 0}, {9: 0}, {3: 0}],
    'idx_map': [0, 1, 2, 3, 0, 0, 0, 3, 3, 3],
    'original_graph_len': 4,
}


if converted == expected:
    print("Constant Degree Conversion Test: PASS")
else:
    print("Constant Degree Conversion Test: FAIL")


