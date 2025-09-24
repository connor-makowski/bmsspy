
import random
from pamda.pamda_timer import pamda_timer

from bmsspy.quicksplit import quicksplit, sortsplit



random.seed(42)
tests = [
    [random.random() for _ in range(10)],
    [random.random() for _ in range(1_000)],
    [random.random() for _ in range(1_000_000)],
    [random.random() for _ in range(10_000_000)],
]

for data in tests:

    # Validate correctness
    quicksplit_output = quicksplit(data)
    sortsplit_output = sortsplit(data)
    assert sorted(quicksplit_output['lower']) == sortsplit_output['lower'], f"Mismatch for Quickselect lower: {quicksplit_output['lower']} != {sortsplit_output['lower']}"
    assert sorted(quicksplit_output['higher']) == sortsplit_output['higher'], f"Mismatch for Quickselect higher: {quicksplit_output['higher']} != {sortsplit_output['higher']}"

    # Benchmark performance
    qs_time = pamda_timer(quicksplit, iterations = 3).get_time_stats(arr=data)
    ss_time = pamda_timer(sortsplit, iterations = 3).get_time_stats(arr=data)
    print(f"n={len(data)}, QS Time: {qs_time['avg']:.2f} ms, SS Time: {ss_time['avg']:.2f} ms, Speedup: {ss_time['avg']/qs_time['avg']:.2f}x")