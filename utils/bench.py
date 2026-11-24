#!/usr/bin/env python3
"""
Quick BMSSP benchmark script.
Benchmarks bmssp, bmssp_cd, bmssp_cpp, and bmssp_cpp_cd across:
- Geograph Marnet
- Geograph World Highways
- GridGraph 50x50 (u5 and o5 with bltr routing)
- GridGraph 100x100 (u5 and o5 with bltr routing)

Outputs results to console and writes a formatted benchmark.md file.
"""

from __future__ import annotations

import argparse
import datetime
import math
import os
import platform
import statistics
import sys
import time
from pathlib import Path

# Add repo root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from scgraph import GeoGraph, GridGraph  # noqa: E402
from bmsspy import Bmssp, has_cpp  # noqa: E402

try:
    from bmsspy import BmsspC
except ImportError:
    BmsspC = None


def make_gridgraph(size: int, mode: str = "u5") -> GridGraph:
    """
    Construct a square grid graph with a barrier down the center.
    - 'u5': Barrier from y=5 to y=size (gap of 5 at the bottom).
    - 'o5': Barrier from y=0 to y=size-5 (gap of 5 at the top).
    """
    half_x = int(size / 2)
    if mode == "u5":
        blocks = [(half_x, i) for i in range(5, size)]
    elif mode == "o5":
        blocks = [(half_x, i) for i in range(0, size - 5)]
    else:
        blocks = []

    shape = [(0, 0), (0, 1), (1, 0), (1, 1)]
    return GridGraph(
        x_size=size,
        y_size=size,
        blocks=blocks,
        shape=shape,
        add_exterior_walls=False,
    )


ALL_ALGOS = ["bmssp", "bmssp_cd", "bmssp_cpp", "bmssp_cpp_cd"]


def create_solver(algo: str, graph: list[dict] | list[list[dict]]):
    if algo == "bmssp":
        return Bmssp(graph=graph, use_constant_degree_graph=False)
    elif algo == "bmssp_cd":
        return Bmssp(graph=graph, use_constant_degree_graph=True)
    elif algo == "bmssp_cpp":
        if not has_cpp():
            raise RuntimeError("C++ extension BmsspC is not available.")
        return BmsspC(graph=graph, use_constant_degree_graph=False)
    elif algo == "bmssp_cpp_cd":
        if not has_cpp():
            raise RuntimeError("C++ extension BmsspC is not available.")
        return BmsspC(graph=graph, use_constant_degree_graph=True)
    else:
        raise ValueError(f"Unknown algorithm: {algo}")


def benchmark_algo(
    solver,
    origin_id: int,
    runs: int = 5,
    verbose: bool = False,
) -> dict:
    """Warmup 1 run, then execute `runs` iterations."""
    # Warmup
    solver.solve(origin_id=origin_id)

    times_ms: list[float] = []
    for _ in range(runs):
        t0 = time.perf_counter()
        solver.solve(origin_id=origin_id)
        dt_ms = (time.perf_counter() - t0) * 1000.0
        times_ms.append(dt_ms)

    avg_ms = statistics.mean(times_ms)
    std_ms = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
    min_ms = min(times_ms)
    max_ms = max(times_ms)

    return {
        "avg": avg_ms,
        "std": std_ms,
        "min": min_ms,
        "max": max_ms,
        "raw": times_ms,
    }


def get_test_cases(graphs_filter: str = "all") -> list[dict]:
    filter_list = (
        [g.strip().lower() for g in graphs_filter.split(",")]
        if graphs_filter != "all"
        else None
    )

    def is_included(key: str, name: str) -> bool:
        if filter_list is None:
            return True
        return any(
            gf in key.lower() or gf in name.lower() for gf in filter_list
        )

    cases = []

    # 1. Geograph Marnet
    if is_included("marnet", "Geograph Marnet"):
        print("Loading Geograph Marnet...")
        marnet = GeoGraph.load_geograph("marnet")
        marnet_origin = marnet.geokdtree.closest_idx([34.0522, -118.2437])  # LA
        cases.append(
            {
                "key": "marnet",
                "name": "Geograph Marnet",
                "case": "los_angeles",
                "graph": marnet.graph,
                "origin": marnet_origin,
                "nodes": len(marnet.graph),
                "edges": sum(len(n) for n in marnet.graph),
            }
        )

    # 2. Geograph World Highways
    if is_included("world_highways", "Geograph World Highways"):
        print("Loading Geograph World Highways...")
        wh = GeoGraph.load_geograph("world_highways")
        wh_origin = wh.geokdtree.closest_idx([34.0522, -118.2437])  # LA
        cases.append(
            {
                "key": "world_highways",
                "name": "Geograph World Highways",
                "case": "los_angeles",
                "graph": wh.graph,
                "origin": wh_origin,
                "nodes": len(wh.graph),
                "edges": sum(len(n) for n in wh.graph),
            }
        )

    # 3. GridGraph 50x50 u5 (bltr)
    if is_included("grid50_u5", "GridGraph 50x50 u5") or is_included(
        "grid50", "GridGraph 50x50"
    ):
        print("Creating GridGraph 50x50 u5...")
        g50_u5 = make_gridgraph(50, mode="u5")
        cases.append(
            {
                "key": "grid50_u5",
                "name": "GridGraph 50x50",
                "case": "u5 (bltr)",
                "graph": g50_u5.graph,
                "origin": g50_u5.get_idx(x=5, y=5),
                "nodes": len(g50_u5.graph),
                "edges": sum(len(n) for n in g50_u5.graph),
            }
        )

    # 4. GridGraph 50x50 o5 (bltr)
    if is_included("grid50_o5", "GridGraph 50x50 o5") or is_included(
        "grid50", "GridGraph 50x50"
    ):
        print("Creating GridGraph 50x50 o5...")
        g50_o5 = make_gridgraph(50, mode="o5")
        cases.append(
            {
                "key": "grid50_o5",
                "name": "GridGraph 50x50",
                "case": "o5 (bltr)",
                "graph": g50_o5.graph,
                "origin": g50_o5.get_idx(x=5, y=5),
                "nodes": len(g50_o5.graph),
                "edges": sum(len(n) for n in g50_o5.graph),
            }
        )

    # 5. GridGraph 100x100 u5 (bltr)
    if is_included("grid100_u5", "GridGraph 100x100 u5") or is_included(
        "grid100", "GridGraph 100x100"
    ):
        print("Creating GridGraph 100x100 u5...")
        g100_u5 = make_gridgraph(100, mode="u5")
        cases.append(
            {
                "key": "grid100_u5",
                "name": "GridGraph 100x100",
                "case": "u5 (bltr)",
                "graph": g100_u5.graph,
                "origin": g100_u5.get_idx(x=5, y=5),
                "nodes": len(g100_u5.graph),
                "edges": sum(len(n) for n in g100_u5.graph),
            }
        )

    # 6. GridGraph 100x100 o5 (bltr)
    if is_included("grid100_o5", "GridGraph 100x100 o5") or is_included(
        "grid100", "GridGraph 100x100"
    ):
        print("Creating GridGraph 100x100 o5...")
        g100_o5 = make_gridgraph(100, mode="o5")
        cases.append(
            {
                "key": "grid100_o5",
                "name": "GridGraph 100x100",
                "case": "o5 (bltr)",
                "graph": g100_o5.graph,
                "origin": g100_o5.get_idx(x=5, y=5),
                "nodes": len(g100_o5.graph),
                "edges": sum(len(n) for n in g100_o5.graph),
            }
        )

    return cases


def format_ms(val: float | None) -> str:
    if val is None or math.isnan(val):
        return "N/A"
    if val < 1.0:
        return f"{val:.2f} ms"
    if val < 1000.0:
        return f"{val:.1f} ms"
    return f"{val / 1000.0:.2f} s"


def generate_markdown_report(
    results: list[dict],
    selected_algos: list[str],
    runs: int,
) -> str:
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    python_ver = platform.python_version()
    cpp_status = "Available (compiled)" if has_cpp() else "Not available"

    lines = [
        "# BMSSP Benchmark Report",
        "",
        f"- **Date**: {now_str}",
        f"- **Runs per test**: {runs} (after 1 warmup run)",
        f"- **Platform**: {platform.system()} {platform.machine()} ({platform.platform()})",
        f"- **Python Version**: {python_ver}",
        f"- **C++ Extension (`BmsspC`)**: {cpp_status}",
        "",
        "## Summary Results",
        "",
    ]

    # Header
    headers = ["Graph", "Case / Style", "Nodes", "Edges"]
    for a in selected_algos:
        headers.append(a)

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for r in results:
        row = [
            r["name"],
            r["case"],
            f"{r['nodes']:,}",
            f"{r['edges']:,}",
        ]
        for a in selected_algos:
            data = r.get("algos", {}).get(a)
            if data:
                row.append(format_ms(data["avg"]))
            else:
                row.append("N/A")
        lines.append("| " + " | ".join(row) + " |")

    # Detailed statistics table
    lines.extend(
        [
            "",
            "## Detailed Statistics",
            "",
            "| Graph | Case | Algorithm | Mean | Min | Max | Stdev |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    for r in results:
        for a in selected_algos:
            data = r.get("algos", {}).get(a)
            if data:
                lines.append(
                    f"| {r['name']} | {r['case']} | {a} | "
                    f"{format_ms(data['avg'])} | {format_ms(data['min'])} | "
                    f"{format_ms(data['max'])} | {format_ms(data['std'])} |"
                )

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Run quick BMSSP benchmarks across key graphs."
    )
    parser.add_argument(
        "-n",
        "--runs",
        type=int,
        default=5,
        help="Number of timed iterations per algorithm (default: 5).",
    )
    parser.add_argument(
        "--graphs",
        type=str,
        default="all",
        help="Comma-separated graphs filter (e.g. 'marnet,grid50' or 'all').",
    )
    parser.add_argument(
        "--algos",
        type=str,
        default="all",
        help="Comma-separated algorithms ('bmssp,bmssp_cd,bmssp_cpp,bmssp_cpp_cd', 'cpp', 'py', or 'all').",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=str(root_dir / "benchmark.md"),
        help="Path to output markdown report (default: benchmark.md).",
    )
    parser.add_argument(
        "--no-file",
        action="store_true",
        help="Print to stdout only, do not write markdown file.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose logging of individual run times.",
    )

    args = parser.parse_args()

    # Determine algorithms to run
    if args.algos == "all":
        selected_algos = list(ALL_ALGOS)
    elif args.algos == "cpp":
        selected_algos = ["bmssp_cpp", "bmssp_cpp_cd"]
    elif args.algos == "py":
        selected_algos = ["bmssp", "bmssp_cd"]
    else:
        req = [x.strip() for x in args.algos.split(",")]
        selected_algos = [x for x in req if x in ALL_ALGOS]

    if not has_cpp():
        print("Note: C++ extension not found. Skipping C++ algorithms.")
        selected_algos = [
            a
            for a in selected_algos
            if not a.endswith("cpp") and not "cpp" in a
        ]

    print("\n" + "=" * 60)
    print("BMSSP Quick Benchmarker")
    print(f"Runs: {args.runs} per algorithm")
    print(f"Algorithms: {', '.join(selected_algos)}")
    print("=" * 60 + "\n")

    test_cases = get_test_cases(args.graphs)

    results = []

    for tc in test_cases:
        print(f"\n--- Benchmarking: {tc['name']} ({tc['case']}) ---")
        print(
            f"Nodes: {tc['nodes']:,} | Edges: {tc['edges']:,} | Origin: {tc['origin']}"
        )

        tc_result = {
            "name": tc["name"],
            "case": tc["case"],
            "nodes": tc["nodes"],
            "edges": tc["edges"],
            "algos": {},
        }

        for algo in selected_algos:
            sys.stdout.write(f"  {algo:<16} ... ")
            sys.stdout.flush()

            try:
                t0_init = time.perf_counter()
                solver = create_solver(algo, tc["graph"])
                init_ms = (time.perf_counter() - t0_init) * 1000.0

                stats = benchmark_algo(
                    solver=solver,
                    origin_id=tc["origin"],
                    runs=args.runs,
                    verbose=args.verbose,
                )
                tc_result["algos"][algo] = stats

                print(
                    f"{format_ms(stats['avg']):>9} "
                    f"(min: {format_ms(stats['min'])}, max: {format_ms(stats['max'])}, init: {format_ms(init_ms)})"
                )
            except Exception as e:
                print(f"FAILED: {e}")

        results.append(tc_result)

    # Generate Markdown Report
    md_content = generate_markdown_report(results, selected_algos, args.runs)

    print("\n" + "=" * 60)
    print("Benchmark Complete! Summary Table:")
    print("=" * 60 + "\n")
    # Print the table portion of markdown to console
    table_lines = [
        line for line in md_content.splitlines() if line.startswith("|")
    ]
    print("\n".join(table_lines[: len(results) + 2]))

    if not args.no_file:
        out_path = Path(args.output)
        out_path.write_text(md_content, encoding="utf-8")
        print(f"\nWrote full benchmark report to: {out_path}")


if __name__ == "__main__":
    main()
