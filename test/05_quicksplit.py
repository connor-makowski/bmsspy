import random
from pamda.pamda_timer import pamda_timer

from bmsspy.helpers.quicksplit import quicksplit, sortsplit, quicksplit_dict

print("\n===============\nQuicksplit Tests:\n===============")

try:
    from bmsspy.bin.quicksplit_cpp import quicksplit_dict as quicksplit_dict_cpp
    from bmsspy.bin.quicksplit_cpp import quicksplit as quicksplit_cpp
except ImportError:
    print("C++ QuickSplit bindings not available, skipping C++ tests.")

random.seed(42)
tests = [
    [round(random.random(), 10) for _ in range(10)],
    [round(random.random(), 10) for _ in range(1_000)],
    [round(random.random(), 10) for _ in range(1_000_000)],
]

for data in tests:

    # Validate correctness
    quicksplit_output = quicksplit(data)
    sortsplit_output = sortsplit(data)
    dict_data = {i: v for i, v in enumerate(data)}
    quicksplit_dict_output = quicksplit_dict(dict_data)
    if quicksplit_cpp:
        quicksplit_cpp_output = quicksplit_cpp(data)
        quicksplit_dict_cpp_output = quicksplit_dict_cpp(dict_data)

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

    # if quicksplit_cpp:
    #     assert (
    #         sorted(quicksplit_cpp_output.lower) == sortsplit_output["lower"]
    #     ), f"Mismatch for Quickselect C++ lower: {quicksplit_cpp_output.lower} != {sortsplit_output['lower']}"
    #     assert (
    #         sorted(quicksplit_cpp_output.higher) == sortsplit_output["higher"]
    #     ), f"Mismatch for Quickselect C++ higher: {quicksplit_cpp_output.higher} != {sortsplit_output['higher']}"
    #     assert (
    #         quicksplit_cpp_output.pivot == sortsplit_output["pivot"]
    #     ), f"Mismatch for C++ pivot: {quicksplit_cpp_output.pivot} != {sortsplit_output['pivot']}"
    # if quicksplit_dict_cpp:
    #     assert (
    #         sorted(
    #             [v for k, v in quicksplit_dict_cpp_output.lower.items()]
    #         )
    #         == sortsplit_output["lower"]
    #     ), f"Mismatch for Quickselect Dict C++ lower: {quicksplit_dict_cpp_output.lower} != {sortsplit_output['lower']}"
    #     assert (
    #         sorted(
    #             [v for k, v in quicksplit_dict_cpp_output.higher.items()]
    #         )
    #         == sortsplit_output["higher"]
    #     ), f"Mismatch for Quickselect Dict C++ higher: {quicksplit_dict_cpp_output.higher} != {sortsplit_output['higher']}"
    #     assert (
    #         quicksplit_dict_cpp_output.pivot == sortsplit_output["pivot"]
    #     ), f"Mismatch for C++ Dict pivot: {quicksplit_dict_cpp_output.pivot} != {sortsplit_output['pivot']}"


    # Benchmark performance
    qs_time = pamda_timer(quicksplit, iterations=3).get_time_stats(arr=data)
    ss_time = pamda_timer(sortsplit, iterations=3).get_time_stats(arr=data)
    qsd_time = pamda_timer(quicksplit_dict, iterations=3).get_time_stats(
        data=dict_data
    )
    if quicksplit_cpp:
        qs_time_cpp = pamda_timer(quicksplit_cpp, iterations=3).get_time_stats(
            arr=data
        )
        qsd_time_cpp = pamda_timer(quicksplit_dict_cpp, iterations=3).get_time_stats(
            data=dict_data
        )
        print(
            f"""n={len(data)},
    QS Time: {qs_time['avg']:.4f} ms
    SS Time: {ss_time['avg']:.4f} ms
    QSD Time: {qsd_time['avg']:.4f} ms
    QSC Time: {qs_time_cpp['avg']:.4f} ms
    QSDC Time: {qsd_time_cpp['avg']:.4f} ms

    QS vs SS Speedup: {ss_time['avg']/qs_time['avg']:.4f}x
    QSC vs QS Speedup: {qs_time['avg']/qs_time_cpp['avg']:.4f}x
    QSDC vs QSD Speedup: {qsd_time['avg']/qsd_time_cpp['avg']:.4f}x
""")
    else:
        print(
            f"""n={len(data)}
    QS Time: {qs_time['avg']:.4f} ms
    SS Time: {ss_time['avg']:.4f} ms
    QSD Time: {qsd_time['avg']:.4f} ms 
    QS vs SS Speedup: {ss_time['avg']/qs_time['avg']:.4f}x
""")
