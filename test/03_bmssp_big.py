from bmsspy.solvers import bmssp
from scgraph_data.world_highways import world_highways_geograph

import time

start_time = time.time()
world_highways_geograph.get_shortest_path(
    # Check for route between new york and los angeles
    origin_node={"latitude": 40.71,"longitude": -74.01},
    destination_node={"latitude": 34.05,"longitude": -118.24},
    algorithm_fn=bmssp,
    # algorithm_kwargs={"heuristic_fn": world_highways_geograph.haversine},
)
end_time = time.time()
print(f"BMSSP Big Test: Completed in {(end_time - start_time) * 1000:.2f} ms")