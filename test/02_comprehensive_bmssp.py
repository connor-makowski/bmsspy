from scgraph import GeoGraph, Graph
from scgraph.utils import hard_round
from pamda import pamda
from bmsspy import Bmssp

marnet_graph = GeoGraph.load_geograph("marnet").graph
us_freeway_graph = GeoGraph.load_geograph("us_freeway").graph
# world_highways_and_marnet_graph = GeoGraph.load_geograph(
#     "world_highways_and_marnet"
# ).graph


def validate(realized, expected):
    realized = [
        (
            hard_round(6, float(val))
            if float(val) != float("inf")
            else float("inf")
        )
        for val in realized
    ]
    expected = [
        (
            hard_round(6, float(val))
            if float(val) != float("inf")
            else float("inf")
        )
        for val in expected
    ]
    assert realized == expected


def check_correctness(graph, origin_id):
    bmssp_graph = Bmssp(graph=graph)
    dm_sp_tree = Graph(graph).get_shortest_path_tree(origin_id=origin_id)
    validate(
        realized=bmssp_graph.solve(origin_id=origin_id)["distance_matrix"],
        expected=dm_sp_tree["distance_matrix"][: len(graph)],
    )

    bmssp_no_cd = Bmssp(graph=graph, use_constant_degree_graph=False)
    dm_sp_tree_no_cd = Graph(graph).get_shortest_path_tree(origin_id=origin_id)
    validate(
        realized=bmssp_no_cd.solve(origin_id=origin_id)["distance_matrix"],
        expected=dm_sp_tree_no_cd["distance_matrix"][: len(graph)],
    )


def test_comprehensive_bmssp():
    graph = [
        {1: 5, 2: 1},
        {0: 5, 2: 2, 3: 1},
        {0: 1, 1: 2, 3: 4, 4: 8},
        {1: 1, 2: 4, 4: 3, 5: 6},
        {2: 8, 3: 3},
        {3: 6},
    ]

    check_correctness(graph=graph, origin_id=1)
    check_correctness(graph=marnet_graph, origin_id=1)
    check_correctness(graph=us_freeway_graph, origin_id=1)
    # check_correctness(graph=world_highways_and_marnet_graph, origin_id=1)


def test_bmssp_time():
    marnet_graph_bmssp = Bmssp(graph=marnet_graph)
    us_freeway_graph_bmssp = Bmssp(graph=us_freeway_graph)
    # world_highways_and_marnet_graph_bmssp = Bmssp(
    #     graph=world_highways_and_marnet_graph
    # )

    marnet_graph_bmssp_no_cd = Bmssp(
        graph=marnet_graph, use_constant_degree_graph=False
    )
    us_freeway_graph_bmssp_no_cd = Bmssp(
        graph=us_freeway_graph, use_constant_degree_graph=False
    )
    # world_highways_and_marnet_graph_bmssp_no_cd = Bmssp(
    #     graph=world_highways_and_marnet_graph, use_constant_degree_graph=False
    # )

    marnet_graph_bmssp.solve(origin_id=0, destination_id=5)
    marnet_graph_bmssp.solve(origin_id=100, destination_id=7999)
    marnet_graph_bmssp.solve(origin_id=4022, destination_id=8342)

    us_freeway_graph_bmssp.solve(origin_id=0, destination_id=5)
    us_freeway_graph_bmssp.solve(origin_id=4022, destination_id=8342)

    # world_highways_and_marnet_graph_bmssp.solve(origin_id=0, destination_id=5)
    # world_highways_and_marnet_graph_bmssp_no_cd.solve(
    #     origin_id=0, destination_id=5
    # )

    Graph(marnet_graph).get_shortest_path_tree(origin_id=0)
    Graph(us_freeway_graph).get_shortest_path_tree(origin_id=0)
    # Graph(world_highways_and_marnet_graph).get_shortest_path_tree(origin_id=0)


if __name__ == "__main__":
    import time

    print("\n===============\nBMSSP VS SCGraph Tests:\n===============")

    def validate_print(name, realized, expected):
        realized = [
            (
                hard_round(6, float(val))
                if float(val) != float("inf")
                else float("inf")
            )
            for val in realized
        ]
        expected = [
            (
                hard_round(6, float(val))
                if float(val) != float("inf")
                else float("inf")
            )
            for val in expected
        ]
        if realized == expected:
            print(f"{name}: PASS")
        else:
            print(f"{name}: FAIL")

    def check_correctness_print(name, graph, origin_id):
        bmssp_graph = Bmssp(graph=graph)
        dm_sp_tree = Graph(graph).get_shortest_path_tree(origin_id=origin_id)
        validate_print(
            name=name + " (Standard)",
            realized=bmssp_graph.solve(origin_id=origin_id)["distance_matrix"],
            expected=dm_sp_tree["distance_matrix"][: len(graph)],
        )

        bmssp_no_cd = Bmssp(graph=graph, use_constant_degree_graph=False)
        dm_sp_tree_no_cd = Graph(graph).get_shortest_path_tree(origin_id=origin_id)
        validate_print(
            name=name + "(Not Constant Degree)",
            realized=bmssp_no_cd.solve(origin_id=origin_id)["distance_matrix"],
            expected=dm_sp_tree_no_cd["distance_matrix"][: len(graph)],
        )

    def time_test(name, thunk):
        start = time.time()
        thunk()
        print(f"{name}: {round((time.time()-start)*1000, 4)}ms")

    graph = [
        {1: 5, 2: 1},
        {0: 5, 2: 2, 3: 1},
        {0: 1, 1: 2, 3: 4, 4: 8},
        {1: 1, 2: 4, 4: 3, 5: 6},
        {2: 8, 3: 3},
        {3: 6},
    ]

    check_correctness_print("BMSSP Basic Graph Distance Matrix", graph, 1)
    check_correctness_print(
        "BMSSP Marnet Graph Distance Matrix", marnet_graph, 1
    )
    check_correctness_print(
        "BMSSP US Freeway Graph Distance Matrix", us_freeway_graph, 1
    )
    # check_correctness_print(
    #     "BMSSP World Highways and Marnet Graph Distance Matrix",
    #     world_highways_and_marnet_graph,
    #     1,
    # )

    print("\n===============\nBMSSP Time Tests:\n===============")

    marnet_graph_bmssp = Bmssp(graph=marnet_graph)
    us_freeway_graph_bmssp = Bmssp(graph=us_freeway_graph)
    # world_highways_and_marnet_graph_bmssp = Bmssp(
    #     graph=world_highways_and_marnet_graph
    # )

    marnet_graph_bmssp_no_cd = Bmssp(
        graph=marnet_graph, use_constant_degree_graph=False
    )
    us_freeway_graph_bmssp_no_cd = Bmssp(
        graph=us_freeway_graph, use_constant_degree_graph=False
    )
    # world_highways_and_marnet_graph_bmssp_no_cd = Bmssp(
    #     graph=world_highways_and_marnet_graph, use_constant_degree_graph=False
    # )

    time_test(
        "BMSSP 1 (marnet)",
        pamda.thunkify(marnet_graph_bmssp.solve)(origin_id=0, destination_id=5),
    )
    time_test(
        "BMSSP 2 (marnet)",
        pamda.thunkify(marnet_graph_bmssp.solve)(
            origin_id=100, destination_id=7999
        ),
    )
    time_test(
        "BMSSP 3 (marnet)",
        pamda.thunkify(marnet_graph_bmssp.solve)(
            origin_id=4022, destination_id=8342
        ),
    )
    time_test(
        "BMSSP 4 (us_freeway)",
        pamda.thunkify(us_freeway_graph_bmssp.solve)(
            origin_id=0, destination_id=5
        ),
    )
    time_test(
        "BMSSP 5 (us_freeway)",
        pamda.thunkify(us_freeway_graph_bmssp.solve)(
            origin_id=4022, destination_id=8342
        ),
    )
    # time_test(
    #     "BMSSP 6 (world_highways_and_marnet)",
    #     pamda.thunkify(world_highways_and_marnet_graph_bmssp.solve)(
    #         origin_id=0, destination_id=5
    #     ),
    # )
    # time_test(
    #     "BMSSP 7 (not constant degree) (world_highways_and_marnet)",
    #     pamda.thunkify(world_highways_and_marnet_graph_bmssp_no_cd.solve)(
    #         origin_id=0, destination_id=5
    #     ),
    # )

    marnet_graph_obj = Graph(marnet_graph)
    us_freeway_graph_obj = Graph(us_freeway_graph)
    # world_highways_and_marnet_graph_obj = Graph(world_highways_and_marnet_graph)

    time_test(
        "Shortest Path Tree Comparison (marnet)",
        lambda: marnet_graph_obj.get_shortest_path_tree(origin_id=0),
    )
    time_test(
        "Shortest Path Tree Comparison (us_freeway)",
        lambda: us_freeway_graph_obj.get_shortest_path_tree(origin_id=0),
    )
    # time_test(
    #     "Shortest Path Tree Comparison (world_highways)",
    #     lambda: Graph(world_highways_and_marnet_graph).get_shortest_path_tree(origin_id=0),
    # )
