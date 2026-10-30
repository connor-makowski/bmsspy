from scgraph import GeoGraph

# Small Geographs
marnet_geograph = GeoGraph.load_geograph("marnet")
north_america_rail_geograph = GeoGraph.load_geograph("north_america_rail")
oak_ridge_maritime_geograph = GeoGraph.load_geograph("oak_ridge_maritime")
us_freeway_geograph = GeoGraph.load_geograph("us_freeway")

# Large Geographs
world_highways_and_marnet_geograph = GeoGraph.load_geograph("world_highways_and_marnet")
# world_highways_geograph = GeoGraph.load_geograph("world_highways")
# world_railways_geograph = GeoGraph.load_geograph("world_railways")

# Utilities
import platform
import argparse
from pamda import pamda

# Local Imports and Utils
try:
    from utils.graphs import make_nxgraph, make_igraph, make_gridgraph
    from utils.time_case import time_case, update_benchmark_csv, ALL_ALGORITHMS
except ImportError:
    from benchmarking.utils.graphs import make_nxgraph, make_igraph, make_gridgraph
    from benchmarking.utils.time_case import time_case, update_benchmark_csv, ALL_ALGORITHMS


def get_graph_data():
    return [
        # Geographs
        # Small Geographs
        ("Geograph Marnet", marnet_geograph),
        ("Geograph North America Rail", north_america_rail_geograph),
        ("Geograph Oak Ridge Maritime", oak_ridge_maritime_geograph),
        ("Geograph US Freeway", us_freeway_geograph),
        # Large Geographs
        ("Geograph World Highways and Marnet", world_highways_and_marnet_geograph),
        # GridGraphs
        # Square GridGraphs
        ("square_gridgraph_15x15", make_gridgraph(15, 15)),
        ("square_gridgraph_25x25", make_gridgraph(25, 25)),
        ("Square GridGraph 50x50", make_gridgraph(50, 50)),
        ("Square GridGraph 75x75", make_gridgraph(75, 75)),
        ("Square GridGraph 100x100", make_gridgraph(100, 100)),
        ("Square GridGraph 250x250", make_gridgraph(250, 250)),
        ("Square GridGraph 500x500", make_gridgraph(500, 500)),
        ("Square GridGraph 750x750", make_gridgraph(750, 750)),
        ("Square GridGraph 1000x1000", make_gridgraph(1000, 1000)),
        # Rectangular GridGraphs
        ("Rectangular_gridgraph_15x50", make_gridgraph(15, 50)),
        ("Rectangular_gridgraph_25x50", make_gridgraph(25, 50)),
        ("Rectangular GridGraph 25x100", make_gridgraph(25, 100)),
        ("Rectangular GridGraph 50x100", make_gridgraph(50, 100)),
        ("Rectangular GridGraph 50x200", make_gridgraph(50, 200)),
        ("Rectangular GridGraph 100x500", make_gridgraph(100, 500)),
        ("Rectangular GridGraph 100x1000", make_gridgraph(100, 1000)),
        ("Rectangular GridGraph 100x1500", make_gridgraph(100, 1500)),
        ("Rectangular GridGraph 100x2000", make_gridgraph(100, 2000)),
    ]


def run_benchmark(
    algorithms: list[str] | set[str] | None = None,
    graphs: list[str] | None = None,
    iterations: int = 10,
    save_csv: bool = True,
    print_console: bool = True,
) -> list[dict]:
    output = []
    graph_data = get_graph_data()

    if graphs:
        graph_data = [
            (name, obj)
            for name, obj in graph_data
            if any(g.lower() in name.lower() for g in graphs)
        ]

    needs_nx = (algorithms is None) or any(
        a in algorithms for a in ["nx_dijkstra", "nx"]
    )
    needs_ig = (algorithms is None) or any(
        a in algorithms for a in ["ig_dijkstra", "ig"]
    )

    if print_console:
        print("\n===============\nGeneral Time Tests:\n===============")
        if algorithms:
            print(f"Algorithms: {list(algorithms)}")
        if graphs:
            print(f"Graphs filter: {graphs}")
        print(f"Iterations: {iterations}")

    for name, scgraph_object in graph_data:
        if print_console:
            print(f"\n{name}:")
        scgraph = scgraph_object.graph
        nxgraph = make_nxgraph(scgraph) if needs_nx else None
        igraph = make_igraph(scgraph) if needs_ig else None

        # Warmup the GeoKDTree
        try:
            scgraph_object.warmup()
        except Exception:
            pass

        if "gridgraph" in name.lower():
            test_cases = [
                ("bottom_left", scgraph_object.get_idx(**{"x": 5, "y": 5})),
                (
                    "top_right",
                    scgraph_object.get_idx(
                        **{
                            "x": scgraph_object.x_size - 5,
                            "y": scgraph_object.y_size - 5,
                        }
                    ),
                ),
                (
                    "center",
                    scgraph_object.get_idx(
                        **{
                            "x": int(scgraph_object.x_size / 2) - 5,
                            "y": int(scgraph_object.y_size / 2),
                        }
                    ),
                ),
            ]
        else:
            test_cases = [
                (
                    "los_angeles",
                    scgraph_object.geokdtree.closest_idx([34.0522, -118.2437]),
                ),
                (
                    "new_york",
                    scgraph_object.geokdtree.closest_idx([40.7128, -74.0060]),
                ),
                (
                    "seattle",
                    scgraph_object.geokdtree.closest_idx([47.6062, -122.3321]),
                ),
            ]

        for case_name, origin in test_cases:
            output.append(
                time_case(
                    graph_name=name,
                    case_name=case_name,
                    origin=origin,
                    scgraph=scgraph,
                    nxgraph=nxgraph,
                    igraph=igraph,
                    test_vanilla_dijkstra=True,
                    print_console=print_console,
                    iterations=iterations,
                    algorithms=algorithms,
                )
            )

    if save_csv:
        if platform.python_implementation() == "PyPy":
            csv_path = "benchmarking/outputs/pypy_benchmark_time_tests.csv"
        else:
            csv_path = "benchmarking/outputs/benchmark_time_tests.csv"

        update_benchmark_csv(
            filename=csv_path,
            new_results=output,
            selected_algorithms=algorithms,
        )
        if print_console:
            print(f"\nUpdated benchmark results in {csv_path}")

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run BMSSP general time benchmarks."
    )
    parser.add_argument(
        "-a",
        "--algorithms",
        nargs="+",
        default=None,
        help="Specific algorithms to run (e.g. bmssp_cpp bmssp_solve bmssp_constant_degree_cpp_solve bmssp_constant_degree_solve). Default: all.",
    )
    parser.add_argument(
        "-g",
        "--graphs",
        nargs="+",
        default=None,
        help="Specific graph names or substrings to run (e.g. marnet 'Square GridGraph 50x50'). Default: all.",
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=10,
        help="Number of iterations per test case (default: 10).",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Do not save/update the output CSV file.",
    )
    args = parser.parse_args()

    run_benchmark(
        algorithms=args.algorithms,
        graphs=args.graphs,
        iterations=args.iterations,
        save_csv=not args.no_save,
        print_console=True,
    )