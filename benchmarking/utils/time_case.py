# SCGraph Utils
from scgraph.spanning import SpanningTree as SCSpanning
# Other Utilities
from pamda.pamda_timer import pamda_timer

# Local Imports and Utils
from bmsspy.entrypoint import Bmssp
from .graphs import get_nx_shortest_path, get_igraph_shortest_path
from .vanilla_dijkstra import vanilla_dijkstra
from .sc_dijkstra import pure_python_sc_dijkstra, pure_python_heapdict_sc_dijkstra
from bmsspy.data_structures.heap_data_structure import BmsspHeapDataStructure


vanilla_limit = 80000
nx_limit = 1000000
ig_limit = 1000000

def run_algo(algo_key:str, algo_func, algo_kwargs:dict, output:dict, do_run:bool=True, iterations:int=10, print_console:bool=True):
    if do_run:
        algo_time_stats = pamda_timer(algo_func, iterations = iterations).get_time_stats(**algo_kwargs)
        output[algo_key+"_time_ms"] = algo_time_stats['avg']
        output[algo_key+"_stdev"] = algo_time_stats['std']
        output['raw'][algo_key] = algo_time_stats['raw']
        if print_console:
            print(f"{algo_key} time: {algo_time_stats['avg']:.2f} ms (stdev: {algo_time_stats['std']:.2f})")
    else:
        output[algo_key+"_time_ms"] = float('nan')
        output[algo_key+"_stdev"] = float('nan')
        output['raw'][algo_key] = []

def time_case(graph_name, case_name, origin, scgraph, nxgraph=None, igraph=None, test_vanilla_dijkstra:bool=False, print_console:bool=True, iterations:int=10):


    bmssp_graph = Bmssp(graph = scgraph)
    constant_degree_scgraph = bmssp_graph.constant_degree_dict['graph']

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
        algo_key = 'bmssp_solve',
        algo_func = bmssp_graph.solve,
        algo_kwargs = {'origin_id': origin},
        output = output,
        do_run = True,
        iterations = iterations,
        print_console = print_console
    )
    # BMSSP with Heap Timing
    run_algo(
        algo_key = 'bmssp_heap_solve',
        algo_func = bmssp_graph.solve,
        algo_kwargs = {'origin_id': origin, 'data_structure': BmsspHeapDataStructure},
        output = output,
        do_run = True,
        iterations = iterations,
        print_console = print_console
    )
    # SCGraph Dijkstra on Constant Degree Graph Timing
    run_algo(
        algo_key = 'sc_dijkstra_constant_degree',
        algo_func = SCSpanning.makowskis_spanning_tree,
        algo_kwargs = {'graph': constant_degree_scgraph, 'node_id': origin},
        output = output,
        do_run = True,
        iterations = iterations,
        print_console = print_console
    )


    # Regular Graph Timing for Comparison
    # Vanilla Dijkstra Timing
    run_algo(
        algo_key = 'vanilla_dijkstra',
        algo_func = vanilla_dijkstra,
        algo_kwargs = {'graph': scgraph, 'origin_id': origin},
        output = output,
        do_run = test_vanilla_dijkstra and len(scgraph) <= vanilla_limit,
        iterations = iterations,
        print_console = print_console
    )


    # SCGraph Dijkstra Timing
    run_algo(
        algo_key = 'sc_dijkstra',
        algo_func = SCSpanning.makowskis_spanning_tree,
        algo_kwargs = {'graph': scgraph, 'node_id': origin},
        output = output,
        do_run = True,
        iterations = iterations,
        print_console = print_console
    )

    # Pure Python SCGraph Dijkstra Timing to compare apples to apples with BMSSPy
    run_algo(
        algo_key = 'pure_python_sc_dijkstra',
        algo_func = pure_python_sc_dijkstra,
        algo_kwargs = {'graph': scgraph, 'node_id': origin},
        output = output,
        do_run = True,
        iterations = iterations,
        print_console = print_console
    )

    # Pure Python SCGraph Dijkstra with HeapDict Timing to compare apples to apples with BMSSPy
    run_algo(
        algo_key = 'pure_python_heapdict_sc_dijkstra',
        algo_func = pure_python_heapdict_sc_dijkstra,
        algo_kwargs = {'graph': scgraph, 'node_id': origin},
        output = output,
        do_run = True,
        iterations = iterations,
        print_console = print_console
    )

    # NetworkX Dijkstra Timing
    run_algo(
        algo_key = 'nx_dijkstra',
        algo_func = get_nx_shortest_path,
        algo_kwargs = {'graph': nxgraph, 'origin': origin},
        output = output,
        do_run = nxgraph is not None and len(scgraph) <= nx_limit,
        iterations = iterations,
        print_console = print_console
    )

    # iGraph Dijkstra Timing
    run_algo(
        algo_key = 'ig_dijkstra',
        algo_func = get_igraph_shortest_path,
        algo_kwargs = {'graph': igraph, 'origin': origin},
        output = output,
        do_run = igraph is not None and len(scgraph) <= ig_limit,
        iterations = iterations,
        print_console = print_console
    )

    # Reorganize raw data to be at the end
    raw = output.pop('raw')
    output['raw'] = raw
    

    return output