from scgraph import GeoGraph
from bmsspy import Bmssp, BmsspC
import platform
import os
import argparse
from pamda import pamda
from pamda.pamda_timer import pamda_timer

try:
    from utils.graphs import make_gridgraph
except ImportError:
    from benchmarking.utils.graphs import make_gridgraph

# ==========================================
# Available Algorithms and Graphs
# ==========================================
AVAILABLE_ALGORITHMS = {
    "bmssp": (Bmssp, False),
    "bmssp_cpp": (BmsspC, False),
    "bmssp_constant_degree": (Bmssp, True),
    "bmssp_constant_degree_cpp": (BmsspC, True),
}

ALGO_ALIASES = {
    "bmssp_cd": "bmssp_constant_degree",
    "bmssp_cd_cpp": "bmssp_constant_degree_cpp",
    "bmssp_cpp_cd": "bmssp_constant_degree_cpp",
    "bmssp_c": "bmssp_cpp",
}


def normalize_algo(name: str) -> str:
    cleaned = name.strip()
    return ALGO_ALIASES.get(cleaned, cleaned)


def get_base_graphs():
    marnet_geograph = GeoGraph.load_geograph("marnet")
    world_highways_geograph = GeoGraph.load_geograph("world_highways")
    gridgraph_100x100 = make_gridgraph(100, 100)
    gridgraph_200x200 = make_gridgraph(200, 200)
    gridgraph_400x400 = make_gridgraph(400, 400)

    return [
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


def update_precision_benchmark_csv(csv_path: str, new_rows: list[dict]):
    if not os.path.exists(csv_path):
        pamda.write_csv(filename=csv_path, data=new_rows)
        return

    try:
        existing = pamda.read_csv(csv_path)
    except Exception:
        pamda.write_csv(filename=csv_path, data=new_rows)
        return

    existing_map = {}
    order = []
    for r in existing:
        alg = r.get("algorithm", "bmssp")
        r["algorithm"] = alg
        key = (alg, str(r.get("graph_name")), str(r.get("origin_case")))
        existing_map[key] = r
        order.append(key)

    for r in new_rows:
        alg = r.get("algorithm", "bmssp")
        key = (alg, str(r.get("graph_name")), str(r.get("origin_case")))
        if key in existing_map:
            existing_map[key].update(r)
        else:
            existing_map[key] = r
            order.append(key)

    updated_data = [existing_map[k] for k in order]
    pamda.write_csv(filename=csv_path, data=updated_data)


def run_precision_benchmark(
    algorithms: list[str] | set[str] | None = None,
    graphs: list[str] | None = None,
    precisions_to_test: list[int] | None = None,
    iterations: int = 1,
    print_console: bool = True,
    save_csv: bool = True,
) -> list[dict]:
    """
    Run precision benchmark tests for BMSSP on Marnet, World Highways, 100x100, 200x200, and 400x400 GridGraphs.
    Returns a list of dictionaries containing time and distance results.
    """
    output = []
    if algorithms is None:
        selected_algos = ["bmssp"]
    else:
        selected_algos = [normalize_algo(a) for a in algorithms]

    precisions = precisions_to_test if precisions_to_test is not None else [8, 6, 4, 2, 0]
    base_graphs = get_base_graphs()
    if graphs:
        base_graphs = [
            (name, obj, gtype)
            for name, obj, gtype in base_graphs
            if any(g.lower() in name.lower() for g in graphs)
        ]

    if print_console:
        print("\n========================================================")
        print("BMSSP Precision Benchmark Tests")
        print(f"Algorithms: {selected_algos}")
        print(f"Graphs: {[b[0] for b in base_graphs]}")
        print(f"Precisions: {precisions} | Iterations: {iterations}")
        print("========================================================")

    for algo_name in selected_algos:
        if algo_name not in AVAILABLE_ALGORITHMS:
            print(f"Warning: Unknown algorithm '{algo_name}', skipping.")
            continue
        solver_cls, use_cd = AVAILABLE_ALGORITHMS[algo_name]

        if print_console:
            print(f"\n===== Algorithm: {algo_name} =====")

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
                solver_obj = solver_cls(
                    graph=raw_graph, precision=p, use_constant_degree_graph=use_cd
                )

                for origin_name, origin_idx in test_cases.items():
                    # Measure solve time
                    algo_time_stats = pamda_timer(
                        solver_obj.solve, iterations=iterations
                    ).get_time_stats(origin_id=origin_idx)

                    # Solve once for distances
                    res = solver_obj.solve(origin_id=origin_idx)
                    dm = res["distance_matrix"]

                    dist_1 = dm[test_cases[target_1]]
                    dist_2 = dm[test_cases[target_2]]
                    dist_3 = dm[test_cases[target_3]]

                    row = {
                        "algorithm": algo_name,
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

    if print_console and output:
        # Summary OD Table (Pairwise distances and average solve times)
        print("\n========================================================")
        print("Precision Comparison Summary Table:")
        print("========================================================")
        summary_headers = [
            "Algorithm",
            "Graph",
            "Nodes",
            "Prec",
            "Avg Time (ms)",
            "OD Pair 1 Dist",
            "OD Pair 2 Dist",
            "OD Pair 3 Dist",
        ]

        summary_rows = []
        for algo_name in selected_algos:
            for base_name, graph_obj, graph_type in base_graphs:
                test_cases = get_test_cases(graph_obj, graph_type)
                case_keys = list(test_cases.keys())
                c1, c2, c3 = case_keys[0], case_keys[1], case_keys[2]

                for p in precisions:
                    name = f"{base_name}_p{p}"
                    graph_rows = [
                        r
                        for r in output
                        if r["graph_name"] == name and r.get("algorithm") == algo_name
                    ]
                    if not graph_rows:
                        continue
                    avg_time = sum(r["solve_time_ms"] for r in graph_rows) / len(
                        graph_rows
                    )

                    r_c1 = next((r for r in graph_rows if r["origin_case"] == c1), None)
                    r_c2 = next((r for r in graph_rows if r["origin_case"] == c2), None)

                    if r_c1 and r_c2:
                        d_12 = r_c1["target_2_dist"]
                        d_13 = r_c1["target_3_dist"]
                        d_23 = r_c2["target_3_dist"]

                        summary_rows.append(
                            [
                                algo_name,
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

    if save_csv and output:
        if platform.python_implementation() == "PyPy":
            csv_path = "benchmarking/outputs/pypy_precision_benchmark_tests.csv"
        else:
            csv_path = "benchmarking/outputs/precision_benchmark_tests.csv"

        update_precision_benchmark_csv(csv_path, output)
        if print_console:
            print(f"\nSaved/updated benchmark results in {csv_path}")

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run BMSSP precision benchmark tests."
    )
    parser.add_argument(
        "-a",
        "--algorithms",
        nargs="+",
        default=["bmssp"],
        help="Specific algorithms to run (e.g. bmssp bmssp_cpp bmssp_constant_degree bmssp_constant_degree_cpp). Default: bmssp.",
    )
    parser.add_argument(
        "-g",
        "--graphs",
        nargs="+",
        default=None,
        help="Specific base graphs to run (e.g. marnet world_highways gridgraph_100x100). Default: all.",
    )
    parser.add_argument(
        "-p",
        "--precisions",
        type=int,
        nargs="+",
        default=None,
        help="Specific precisions to test (e.g. 8 6 4 2 0). Default: [8, 6, 4, 2, 0].",
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=1,
        help="Number of iterations per test case (default: 1).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save/update the output CSV file.",
    )
    args = parser.parse_args()

    run_precision_benchmark(
        algorithms=args.algorithms,
        graphs=args.graphs,
        precisions_to_test=args.precisions,
        iterations=args.iterations,
        save_csv=not args.no_save,
        print_console=True,
    )
