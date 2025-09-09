from bmsspy.solvers import bmssp, bmssp_star
from scgraph.geographs.us_freeway import us_freeway_geograph

graph = [{1: 1, 2: 1}, {2: 1, 3: 3}, {3: 1, 4: 2}, {4: 2}, {}]

output = bmssp(
    graph, 
    origin_id=0, 
    destination_id=3
)

star_output = bmssp_star(
    graph, 
    origin_id=0, 
    destination_id=3, 
    heuristic_fn=lambda x, y: 0
)

dm_pass = True
if star_output['distance_matrix'] != output['distance_matrix']:
    dm_pass = False

len_pass = True
if star_output['length'] != output['length']:
    len_pass = False

path_pass = True
if star_output['path'] != output['path']:
    path_pass = False


output_usf = bmssp(
    graph = us_freeway_geograph.graph,
    origin_id=0, 
    destination_id=100
)

star_output_usf = bmssp_star(
    graph = us_freeway_geograph.graph,
    origin_id=0, 
    destination_id=100,
    heuristic_fn=us_freeway_geograph.haversine
)

if not (dm_pass and len_pass and path_pass):
    print("BMSSP* Test: Failed")
else:
    print("BMSSP* Test: Passed")
