# SCGraph Utils
from scgraph.graph import Graph
from scgraph.cpp import Graph as CGraph
# Other Utilities
from pamda.pamda_timer import pamda_timer

# Local Imports and Utils
from bmsspy import Bmssp, BmsspC
from .graphs import get_nx_shortest_path, get_igraph_shortest_path
from .vanilla_dijkstra import vanilla_dijkstra
from .sc_dijkstra import pure_python_sc_dijkstra
from bmsspy.data_structures.unique_data_structure import UniqueBmsspDataStructure


import os
import ast
import math
from pamda import pamda

vanilla_limit = 80_000
nx_limit = 1_000_000
ig_limit = 1_000_000
cd_limit = 1_000_000

ALL_ALGORITHMS = [
    "bmssp_constant_degree_solve",
    "bmssp_constant_degree_cpp_solve",
    "pure_python_sc_dijkstra_constant_degree",
    "bmssp_solve",
    "vanilla_dijkstra",
    "sc_dijkstra",
    "sc_dijkstra_cpp",
    "bmssp_cpp",
    "pure_python_sc_dijkstra",
    "nx_dijkstra",
    "ig_dijkstra",
]

ALGO_ALIASES = {
    "bmssp_cd": "bmssp_constant_degree_solve",
    "bmssp_constant_degree": "bmssp_constant_degree_solve",
    "bmssp_cd_cpp": "bmssp_constant_degree_cpp_solve",
    "bmssp_cpp_cd": "bmssp_constant_degree_cpp_solve",
    "bmssp_constant_degree_cpp": "bmssp_constant_degree_cpp_solve",
    "bmssp": "bmssp_solve",
    "bmssp_c": "bmssp_cpp",
    "sc_cpp": "sc_dijkstra_cpp",
    "sc": "sc_dijkstra",
    "nx": "nx_dijkstra",
    "ig": "ig_dijkstra",
    "vanilla": "vanilla_dijkstra",
}


def normalize_algo_name(name: str) -> str:
    name_clean = name.strip()
    return ALGO_ALIASES.get(name_clean, name_clean)


def update_benchmark_csv(
    filename: str,
    new_results: list[dict],
    selected_algorithms: list[str] | set[str] | None = None,
):
    if not os.path.exists(filename):
        pamda.write_csv(filename=filename, data=new_results)
        return

    try:
        existing_data = pamda.read_csv(filename)
    except Exception:
        pamda.write_csv(filename=filename, data=new_results)
        return

    existing_dict = {}
    order = []
    for row in existing_data:
        key = (str(row.get("graph_name")), str(row.get("case_name")))
        existing_dict[key] = row
        order.append(key)

    if selected_algorithms is not None:
        normalized_selected = {
            normalize_algo_name(a) for a in selected_algorithms
        }
    else:
        normalized_selected = None

    for new_row in new_results:
        key = (str(new_row.get("graph_name")), str(new_row.get("case_name")))
        if key in existing_dict:
            row = existing_dict[key]
            for meta in [
                "graph_nodes",
                "graph_edges",
                "constant_degree_graph_nodes",
                "constant_degree_graph_edges",
                "origin_node",
                "iterations",
            ]:
                if meta in new_row and new_row[meta] is not None:
                    row[meta] = new_row[meta]

            existing_raw = {}
            if "raw" in row and row["raw"]:
                if isinstance(row["raw"], str):
                    try:
                        existing_raw = ast.literal_eval(row["raw"])
                    except Exception:
                        existing_raw = {}
                elif isinstance(row["raw"], dict):
                    existing_raw = row["raw"]

            new_raw = new_row.get("raw", {})
            if isinstance(new_raw, str):
                try:
                    new_raw = ast.literal_eval(new_raw)
                except Exception:
                    new_raw = {}

            if normalized_selected is not None:
                algos_to_update = normalized_selected
            else:
                algos_to_update = {
                    k.replace("_time_ms", "")
                    for k in new_row.keys()
                    if k.endswith("_time_ms")
                    and not (
                        isinstance(new_row[k], float) and math.isnan(new_row[k])
                    )
                }

            for algo in algos_to_update:
                time_key = f"{algo}_time_ms"
                stdev_key = f"{algo}_stdev"
                if time_key in new_row and not (
                    isinstance(new_row[time_key], float)
                    and math.isnan(new_row[time_key])
                ):
                    row[time_key] = new_row[time_key]
                    row[stdev_key] = new_row.get(stdev_key, float("nan"))
                    if algo in new_raw:
                        existing_raw[algo] = new_raw[algo]

            row["raw"] = str(existing_raw)
        else:
            existing_dict[key] = new_row
            order.append(key)

    merged_data = [existing_dict[k] for k in order]
    pamda.write_csv(filename=filename, data=merged_data)


def run_algo(
    algo_key: str,
    algo_func,
    algo_kwargs: dict,
    output: dict,
    do_run: bool = True,
    iterations: int = 10,
    print_console: bool = True,
):
    if do_run and algo_func is not None:
        algo_time_stats = pamda_timer(
            algo_func, iterations=iterations
        ).get_time_stats(**algo_kwargs)
        output[algo_key + "_time_ms"] = algo_time_stats["avg"]
        output[algo_key + "_stdev"] = algo_time_stats["std"]
        output["raw"][algo_key] = algo_time_stats["raw"]
        if print_console:
            print(
                f"{algo_key} time: {algo_time_stats['avg']:.2f} ms (stdev: {algo_time_stats['std']:.2f})"
            )
    else:
        output[algo_key + "_time_ms"] = float("nan")
        output[algo_key + "_stdev"] = float("nan")
        output["raw"][algo_key] = []


def time_case(
    graph_name,
    case_name,
    origin,
    scgraph,
    nxgraph=None,
    igraph=None,
    test_vanilla_dijkstra: bool = False,
    print_console: bool = True,
    iterations: int = 10,
    algorithms: list[str] | set[str] | None = None,
):
    if algorithms is not None:
        algorithms_to_run = {normalize_algo_name(a) for a in algorithms}
    else:
        algorithms_to_run = set(ALL_ALGORITHMS)

    needs_cd = any(
        a in algorithms_to_run
        for a in [
            "bmssp_constant_degree_solve",
            "bmssp_constant_degree_cpp_solve",
            "pure_python_sc_dijkstra_constant_degree",
        ]
    )

    if needs_cd and len(scgraph) <= cd_limit:
        bmssp_graph = Bmssp(graph=scgraph)
        constant_degree_scgraph = bmssp_graph.constant_degree_dict["graph"]
        bmssp_c_graph_cd = (
            BmsspC(graph=scgraph, use_constant_degree_graph=True)
            if "bmssp_constant_degree_cpp_solve" in algorithms_to_run
            else None
        )
    else:
        bmssp_graph = None
        constant_degree_scgraph = []
        bmssp_c_graph_cd = None

    if "bmssp_solve" in algorithms_to_run:
        bmssp_graph_no_cd = Bmssp(
            graph=scgraph, use_constant_degree_graph=False
        )
    else:
        bmssp_graph_no_cd = None

    if "bmssp_cpp" in algorithms_to_run:
        bmssp_c_graph_no_cd = BmsspC(
            graph=scgraph, use_constant_degree_graph=False
        )
    else:
        bmssp_c_graph_no_cd = None

    output = {
        'graph_name': graph_name,
        'case_name': case_name,
        'graph_nodes': len(scgraph),
        'graph_edges': sum(len(neighbors) for neighbors in scgraph),
        'constant_degree_graph_nodes': len(constant_degree_scgraph),
        'constant_degree_graph_edges': sum(len(neighbors) for neighbors in constant_degree_scgraph),
        'origin_node': origin,
        'iterations': iterations,
        'raw':{}
    }

    if print_console:
        print(f"\nTesting {case_name}...")

    # Constant Degree Graph Conversion Timing
    # BMSSP Timing
    run_algo(
        algo_key="bmssp_constant_degree_solve",
        algo_func=bmssp_graph.solve if bmssp_graph else None,
        algo_kwargs={"origin_id": origin},
        output=output,
        do_run=(
            ("bmssp_constant_degree_solve" in algorithms_to_run)
            and (len(scgraph) <= cd_limit)
        ),
        iterations=iterations,
        print_console=print_console,
    )
    # BMSSP C++ with Constant Degree Graph Timing
    run_algo(
        algo_key="bmssp_constant_degree_cpp_solve",
        algo_func=bmssp_c_graph_cd.solve if bmssp_c_graph_cd else None,
        algo_kwargs={"origin_id": origin},
        output=output,
        do_run=(
            ("bmssp_constant_degree_cpp_solve" in algorithms_to_run)
            and (len(scgraph) <= cd_limit)
        ),
        iterations=iterations,
        print_console=print_console,
    )
    # SCGraph Dijkstra on Constant Degree Graph Timing
    run_algo(
        algo_key="pure_python_sc_dijkstra_constant_degree",
        algo_func=pure_python_sc_dijkstra,
        algo_kwargs={"graph": constant_degree_scgraph, "node_id": origin},
        output=output,
        do_run=(
            ("pure_python_sc_dijkstra_constant_degree" in algorithms_to_run)
            and (len(scgraph) <= cd_limit)
        ),
        iterations=iterations,
        print_console=print_console,
    )

    #####################################
    # Regular Graph Timing for Comparison
    #####################################

    # BMSSP without Constant Degree Graph Timing
    run_algo(
        algo_key="bmssp_solve",
        algo_func=bmssp_graph_no_cd.solve if bmssp_graph_no_cd else None,
        algo_kwargs={"origin_id": origin},
        output=output,
        do_run="bmssp_solve" in algorithms_to_run,
        iterations=iterations,
        print_console=print_console,
    )

    # Vanilla Dijkstra Timing
    run_algo(
        algo_key="vanilla_dijkstra",
        algo_func=vanilla_dijkstra,
        algo_kwargs={"graph": scgraph, "origin_id": origin},
        output=output,
        do_run=(
            ("vanilla_dijkstra" in algorithms_to_run)
            and test_vanilla_dijkstra
            and (len(scgraph) <= vanilla_limit)
        ),
        iterations=iterations,
        print_console=print_console,
    )

    # SCGraph Dijkstra Timing
    scgraph_object = (
        Graph(scgraph) if "sc_dijkstra" in algorithms_to_run else None
    )
    run_algo(
        algo_key="sc_dijkstra",
        algo_func=(
            (lambda: scgraph_object.get_shortest_path_tree(origin_id=origin))
            if scgraph_object
            else None
        ),
        algo_kwargs={},
        output=output,
        do_run="sc_dijkstra" in algorithms_to_run,
        iterations=iterations,
        print_console=print_console,
    )

    # SCGraph C++ Timings
    scgraph_cpp_object = (
        CGraph(scgraph) if "sc_dijkstra_cpp" in algorithms_to_run else None
    )
    run_algo(
        algo_key="sc_dijkstra_cpp",
        algo_func=(
            (
                lambda: scgraph_cpp_object.get_shortest_path_tree(
                    origin_id=origin
                )
            )
            if scgraph_cpp_object
            else None
        ),
        algo_kwargs={},
        output=output,
        do_run="sc_dijkstra_cpp" in algorithms_to_run,
        iterations=iterations,
        print_console=print_console,
    )

    # Local BMSSP C++ Timings
    run_algo(
        algo_key="bmssp_cpp",
        algo_func=bmssp_c_graph_no_cd.solve if bmssp_c_graph_no_cd else None,
        algo_kwargs={"origin_id": origin},
        output=output,
        do_run="bmssp_cpp" in algorithms_to_run,
        iterations=iterations,
        print_console=print_console,
    )

    # Pure Python SCGraph Dijkstra Timing to compare apples to apples with BMSSPy
    run_algo(
        algo_key="pure_python_sc_dijkstra",
        algo_func=pure_python_sc_dijkstra,
        algo_kwargs={"graph": scgraph, "node_id": origin},
        output=output,
        do_run="pure_python_sc_dijkstra" in algorithms_to_run,
        iterations=iterations,
        print_console=print_console,
    )

    # NetworkX Dijkstra Timing
    run_algo(
        algo_key="nx_dijkstra",
        algo_func=get_nx_shortest_path,
        algo_kwargs={"graph": nxgraph, "origin": origin},
        output=output,
        do_run=(
            ("nx_dijkstra" in algorithms_to_run)
            and (nxgraph is not None)
            and (len(scgraph) <= nx_limit)
        ),
        iterations=iterations,
        print_console=print_console,
    )

    # iGraph Dijkstra Timing
    run_algo(
        algo_key="ig_dijkstra",
        algo_func=get_igraph_shortest_path,
        algo_kwargs={"graph": igraph, "origin": origin},
        output=output,
        do_run=(
            ("ig_dijkstra" in algorithms_to_run)
            and (igraph is not None)
            and (len(scgraph) <= ig_limit)
        ),
        iterations=iterations,
        print_console=print_console,
    )

    # Reorganize raw data to be at the end
    raw = output.pop("raw")
    output["raw"] = raw

    return output