import random
from pamda.pamda_timer import pamda_timer

from bmsspy.helpers.quicksplit import quicksplit, sortsplit, quicksplit_dict

print("\n===============\nQuicksplit Tests:\n===============")

random.seed(42)
tests = [
    [random.random() for _ in range(10)],
    [random.random() for _ in range(1_000)],
    [random.random() for _ in range(1_000_000)],
]

for data in tests:

    # Validate correctness
    quicksplit_output = quicksplit(data)
    sortsplit_output = sortsplit(data)
    dict_data = {i: v for i, v in enumerate(data)}
    quicksplit_dict_output = quicksplit_dict(dict_data)

    assert (
        sorted(quicksplit_output["lower"]) == sortsplit_output["lower"]
    ), f"Mismatch for Quickselect lower: {quicksplit_output['lower']} != {sortsplit_output['lower']}"
    assert (
        sorted(quicksplit_output["higher"]) == sortsplit_output["higher"]
    ), f"Mismatch for Quickselect higher: {quicksplit_output['higher']} != {sortsplit_output['higher']}"
    assert (
        sorted([v for k, v in quicksplit_dict_output["lower"].items()])
        == sortsplit_output["lower"]
    ), f"Mismatch for Quickselect Dict lower: {quicksplit_output['lower']} != {sortsplit_output['lower']}"
    assert (
        sorted([v for k, v in quicksplit_dict_output["higher"].items()])
        == sortsplit_output["higher"]
    ), f"Mismatch for Quickselect Dict higher: {quicksplit_output['higher']} != {sortsplit_output['higher']}"
    assert (
        quicksplit_output["pivot"] == sortsplit_output["pivot"]
    ), f"Mismatch for pivot: {quicksplit_output['pivot']} != {sortsplit_output['pivot']}"

    # Benchmark performance
    qs_time = pamda_timer(quicksplit, iterations=3).get_time_stats(arr=data)
    ss_time = pamda_timer(sortsplit, iterations=3).get_time_stats(arr=data)
    qsd_time = pamda_timer(quicksplit_dict, iterations=3).get_time_stats(
        data=dict_data
    )
    print(
        f"n={len(data)}, QS Time: {qs_time['avg']:.4f} ms, SS Time: {ss_time['avg']:.4f} ms, Speedup: {ss_time['avg']/qs_time['avg']:.4f}x, QSD Time: {qsd_time['avg']:.4f} ms"
    )
