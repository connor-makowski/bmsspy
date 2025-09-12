
import random
import time
from pamda import pamda
from statistics import mean, stdev

from bmsspy.bmssp_data_structure import BmsspDataStructure

def benchmark(batch_sizes, repeats=30):
    output = []

    for n in batch_sizes:
        # Generate random test data
        pre_key_value_pairs = {(i, random.random()) for i in range(n)}
        key_value_pairs = {(i, random.random()) for i in range(n)}

        results = {
            'items': n,
        }

        # Time batch_prepend
        t_data = []
        for _ in range(repeats):
            ds = BmsspDataStructure(subset_size=10, upper_bound=1e9)
            ds.batch_prepend(pre_key_value_pairs)  # Pre-fill to avoid empty structure
            start = time.perf_counter()
            ds.batch_prepend(key_value_pairs)
            t_data.append((time.perf_counter() - start)*1000)
        results["batch_prepend_ms"] = mean(t_data)
        results["batch_prepend_ms_std"] = stdev(t_data)

        # Time batch_prepend_alt
        t_data = []
        for _ in range(repeats):
            ds = BmsspDataStructure(subset_size=10, upper_bound=1e9)
            ds.batch_prepend_alt(pre_key_value_pairs)  # Pre-fill to avoid empty structure
            start = time.perf_counter()
            ds.batch_prepend_alt(key_value_pairs)
            t_data.append((time.perf_counter() - start)*1000)
        results["batch_prepend_alt_ms"] = mean(t_data)
        results["batch_prepend_alt_ms_std"] = stdev(t_data)

        output.append(results)
    return output


batch_sizes = [1, 2, 5, 10, 100, 1_000, 10_000, 100_000]

output = benchmark(batch_sizes)

pamda.write_csv(
    filename="benchmarking/outputs/data_struct_time_tests.csv",
    data=output
)

for item in output:
    faster = "alt" if item['batch_prepend_alt_ms'] < item['batch_prepend_ms'] else "regular"
    print(f"{item['items']:7d} items | batch_prepend={item['batch_prepend_ms']:.6f}ms | batch_prepend_alt={item['batch_prepend_alt_ms']:.6f}ms → {faster}")