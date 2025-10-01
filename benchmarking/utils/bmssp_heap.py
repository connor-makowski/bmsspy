from bmsspy.bmssp_solver import BmsspSolver
from bmsspy.data_structures.heap_data_structure import BmsspDataStructure

def bmssp_heap(graph: list[dict], node_id: int) -> dict:
    """
    BMSSP solver using the heap-based data structure.
    """
    solver = BmsspSolver(graph, node_id, DataStructure=BmsspDataStructure)
    return {
        "node_id": node_id,
        "predecessors": solver.predecessor,
        "distance_matrix": solver.distance_matrix,
    }