# Local Imports
from bmsspy import Bmssp

print("\n===============\nBasic BMSSP Tests:\n===============")

tiny_graph = Bmssp([{1: 1}, {}])
output = tiny_graph.solve(0)
if output["distance_matrix"] != [0, 1]:
    print("BMSSP Tiny Test: FAIL")
else:
    print("BMSSP Tiny Test: PASS")

graph = Bmssp([{1: 1, 2: 1, 3: 10}, {2: 1, 3: 3, 1: 10}, {3: 1, 4: 2}, {4: 2}, {}])

output = graph.solve(0)
if output["distance_matrix"] != [0, 1, 1, 2, 3]:
    print("BMSSP Test without destination: FAIL")
else:
    print("BMSSP Test without destination: PASS")

output = graph.solve(0, 3)
if output["length"] != 2 or output["path"] != [0, 2, 3]:
    print("BMSSP Test with destination: FAIL")
else:
    print("BMSSP Test with destination: PASS")

zero_weight_graph = Bmssp([{1:0}, {2:0}, {3:0}, {4:0}, {}])

output = zero_weight_graph.solve(0)
if output["distance_matrix"] != [0,0,0,0,0]:
    print("BMSSP Zero-Weight Test: FAIL")
else:
    print("BMSSP Zero-Weight Test: PASS")