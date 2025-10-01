from bmsspy.solvers import bmssp

print("\n===============\nBasic BMSSP Tests:\n===============")

graph = [{1: 1, 2: 1}, {2: 1, 3: 3}, {3: 1, 4: 2}, {4: 2}, {}]
output = bmssp(graph, 0)
if output["distance_matrix"] != [0, 1, 1, 2, 3]:
    print("BMSSP Test without destination: FAIL")
else:
    print("BMSSP Test without destination: PASS")

output = bmssp(graph, 0, 3)
if output["length"] != 2 or output["path"] != [0, 2, 3]:
    print("BMSSP Test with destination: FAIL")
else:
    print("BMSSP Test with destination: PASS")
