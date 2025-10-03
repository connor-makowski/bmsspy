from bmsspy.bmssp_solver import BmsspSolver
from bmsspy.data_structures.heap_data_structure import BmsspDataStructure as HeapDataStructure
from bmsspy.bin.bmssp_data_structure_cpp import BmsspDataStructure as CppDataStructure

def bmssp_heap(graph: list[dict], node_id: int) -> dict:
    """
    BMSSP solver using the heap-based data structure.
    """
    solver = BmsspSolver(graph, node_id, DataStructure=HeapDataStructure)
    return {
        "node_id": node_id,
        "predecessors": solver.predecessor,
        "distance_matrix": solver.distance_matrix,
    }

def bmssp_cpp_ds(graph: list[dict], node_id: int) -> dict:
    """
    BMSSP solver using the C++ data structure.
    """
    solver = BmsspSolver(graph, node_id, DataStructure=CppDataStructure)
    return {
        "node_id": node_id,
        "predecessors": solver.predecessor,
        "distance_matrix": solver.distance_matrix,
    }