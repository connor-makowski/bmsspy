from scgraph import GeoGraph
from bmsspy import Bmssp
import platform
from pamda import pamda
from pamda.pamda_timer import pamda_timer

try:
    from utils.graphs import make_gridgraph
except ImportError:
    from benchmarking.utils.graphs import make_gridgraph

# ==========================================
# Load / Create Graphs
# ==========================================
print("Loading / creating graphs...")
marnet_geograph = GeoGraph.load_geograph("marnet")
world_highways_geograph = GeoGraph.load_geograph("world_highways")
gridgraph_100x100 = make_gridgraph(100, 100)
gridgraph_200x200 = make_gridgraph(200, 200)
gridgraph_400x400 = make_gridgraph(400, 400)

precisions = [8, 6, 4, 2, 0]

# Base graphs for testing
base_graphs = [
    ("marnet", marnet_geograph, "geograph"),
    ("world_highways", world_highways_geograph, "geograph"),
    ("gridgraph_100x100", gridgraph_100x100, "gridgraph"),
    ("gridgraph_200x200", gridgraph_200x200, "gridgraph"),
    ("gridgraph_400x400", gridgraph_400x400, "gridgraph"),
]

# Geograph cities
cities = [
    ("los_angeles", [34.0522, -118.2437]),  # Los Angeles
    ("new_york", [40.7128, -74.0060]),  # New York
    ("seattle", [47.6062, -122.3321]),  # Seattle
]


def get_test_cases(graph_obj, graph_type: str) -> dict[str, int]:
    """Get the origin / target node indices for a graph."""
    if graph_type == "geograph":
        try:
            graph_obj.warmup()
        except Exception:
            pass
        return {
            city_name: graph_obj.geokdtree.closest_idx(coords)
            for city_name, coords in cities
        }
    else:
        return {
            "bottom_left": graph_obj.get_idx(x=5, y=5),
            "top_right": graph_obj.get_idx(
                x=graph_obj.x_size - 5, y=graph_obj.y_size - 5
            ),
            "center": graph_obj.get_idx(
                x=int(graph_obj.x_size / 2) - 5, y=int(graph_obj.y_size / 2)
            ),
        }


def print_table(headers: list[str], rows: list[list]):
    """Format and print an aligned text table."""
    str_rows = [[str(val) for val in row] for row in rows]
    col_widths = [len(h) for h in headers]
    for row in str_rows:
        for i, val in enumerate(row):
            if len(val) > col_widths[i]:
                col_widths[i] = len(val)

    sep_line = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_line = (
        "| "
        + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths))
        + " |"
    )

    print(sep_line)
    print(header_line)
    print(sep_line)
    for row in str_rows:
        row_line = (
            "| "
            + " | ".join(val.ljust(w) for val, w in zip(row, col_widths))
            + " |"
        )
        print(row_line)
    print(sep_line)


def run_precision_benchmark(
    iterations: int = 1, print_console: bool = True, save_csv: bool = True
) -> list[dict]:
    """
    Run precision benchmark tests for BMSSPy on Marnet, World Highways, 100x100, 200x200, and 400x400 GridGraphs.
    Returns a list of dictionaries containing time and distance results.
    """
    output = []

    if print_console:
        print("\n========================================================")
        print("BMSSPy Precision Benchmark Tests")
        print(
            "Graphs: Marnet, World Highways, GridGraphs (100x100, 200x200, 400x400)"
        )
        print(f"Precisions: {precisions} | Iterations: {iterations}")
        print("========================================================")

    for base_name, graph_obj, graph_type in base_graphs:
        test_cases = get_test_cases(graph_obj, graph_type)
        case_keys = list(test_cases.keys())
        target_1, target_2, target_3 = case_keys[0], case_keys[1], case_keys[2]
        raw_graph = graph_obj.graph
        nodes_count = len(raw_graph)

        if print_console:
            print(f"\n--- {base_name} ({nodes_count:,} nodes) ---")

        for p in precisions:
            graph_name = f"{base_name}_p{p}"
            bmssp_obj = Bmssp(
                graph=raw_graph, precision=p, use_constant_degree_graph=False
            )

            for origin_name, origin_idx in test_cases.items():
                # Measure solve time
                algo_time_stats = pamda_timer(
                    bmssp_obj.solve, iterations=iterations
                ).get_time_stats(origin_id=origin_idx)

                # Solve once for distances
                res = bmssp_obj.solve(origin_id=origin_idx)
                dm = res["distance_matrix"]

                dist_1 = dm[test_cases[target_1]]
                dist_2 = dm[test_cases[target_2]]
                dist_3 = dm[test_cases[target_3]]

                row = {
                    "graph_name": graph_name,
                    "base_graph": base_name,
                    "graph_type": graph_type,
                    "nodes": nodes_count,
                    "precision": p,
                    "origin_case": origin_name,
                    "origin_node": origin_idx,
                    "solve_time_ms": algo_time_stats["avg"],
                    "solve_stdev": algo_time_stats["std"],
                    "target_1_name": target_1,
                    "target_1_dist": dist_1,
                    "target_2_name": target_2,
                    "target_2_dist": dist_2,
                    "target_3_name": target_3,
                    "target_3_dist": dist_3,
                    "iterations": iterations,
                    "raw_times": algo_time_stats["raw"],
                }
                output.append(row)

                if print_console:
                    print(
                        f"  {graph_name:<24} | Origin: {origin_name:<12} | "
                        f"Time: {algo_time_stats['avg']:>8.2f} ms | "
                        f"-> {target_1}: {dist_1:>10} | -> {target_2}: {dist_2:>10} | -> {target_3}: {dist_3:>10}"
                    )

    if print_console:
        # Summary OD Table (Pairwise distances and average solve times)
        print("\n========================================================")
        print("Precision Comparison Summary Table:")
        print("========================================================")
        summary_headers = [
            "Graph",
            "Nodes",
            "Prec",
            "Avg Time (ms)",
            "OD Pair 1 Dist",
            "OD Pair 2 Dist",
            "OD Pair 3 Dist",
        ]

        summary_rows = []
        for base_name, graph_obj, graph_type in base_graphs:
            test_cases = get_test_cases(graph_obj, graph_type)
            case_keys = list(test_cases.keys())
            c1, c2, c3 = case_keys[0], case_keys[1], case_keys[2]

            for p in precisions:
                name = f"{base_name}_p{p}"
                graph_rows = [r for r in output if r["graph_name"] == name]
                avg_time = sum(r["solve_time_ms"] for r in graph_rows) / len(
                    graph_rows
                )

                r_c1 = next(r for r in graph_rows if r["origin_case"] == c1)
                r_c2 = next(r for r in graph_rows if r["origin_case"] == c2)

                # Pairwise distances: (c1 -> c2), (c1 -> c3), (c2 -> c3)
                d_12 = r_c1["target_2_dist"]
                d_13 = r_c1["target_3_dist"]
                d_23 = r_c2["target_3_dist"]

                summary_rows.append(
                    [
                        name,
                        f"{r_c1['nodes']:,}",
                        p,
                        f"{avg_time:.2f}",
                        f"{c1}->{c2}: {d_12}",
                        f"{c1}->{c3}: {d_13}",
                        f"{c2}->{c3}: {d_23}",
                    ]
                )

        print_table(summary_headers, summary_rows)

    if save_csv:
        csv_output = [{k: v for k, v in r.items()} for r in output]
        if platform.python_implementation() == "PyPy":
            csv_path = "benchmarking/outputs/pypy_precision_benchmark_tests.csv"
        else:
            csv_path = "benchmarking/outputs/precision_benchmark_tests.csv"

        pamda.write_csv(filename=csv_path, data=csv_output)
        if print_console:
            print(f"\nSaved benchmark results to {csv_path}")

    return output


if __name__ == "__main__":
    run_precision_benchmark(iterations=1, print_console=True, save_csv=True)
