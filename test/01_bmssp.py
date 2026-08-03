from bmsspy import Bmssp


def test_bmssp_tiny():
    tiny_graph = Bmssp([{1: 1}, {}])
    output = tiny_graph.solve(0)
    assert output["distance_matrix"] == [0, 1]


def test_bmssp_no_destination():
    graph = Bmssp(
        [{1: 1, 2: 1, 3: 10}, {2: 1, 3: 3, 1: 10}, {3: 1, 4: 2}, {4: 2}, {}]
    )
    output = graph.solve(0)
    assert output["distance_matrix"] == [0, 1, 1, 2, 3]


def test_bmssp_with_destination():
    graph = Bmssp(
        [{1: 1, 2: 1, 3: 10}, {2: 1, 3: 3, 1: 10}, {3: 1, 4: 2}, {4: 2}, {}]
    )
    output = graph.solve(0, 3)
    assert output["length"] == 2 and output["path"] == [0, 2, 3]


def test_bmssp_zero_weight():
    zero_weight_graph = Bmssp([{1: 0}, {2: 0}, {3: 0}, {4: 0}, {}])
    output = zero_weight_graph.solve(0)
    assert output["distance_matrix"] == [0, 0, 0, 0, 0]


def test_bmssp_zero_weight_2():
    zero_weight_graph2 = Bmssp(
        [
            {1: 0, 2: 0, 3: 0, 4: 0},
            {2: 0, 3: 0},
            {3: 0, 4: 0},
            {4: 0, 0: 0},
            {0: 0, 1: 0},
        ]
    )
    output = zero_weight_graph2.solve(0)
    assert output["distance_matrix"] == [0, 0, 0, 0, 0]


if __name__ == "__main__":
    print("\n===============\nBasic BMSSP Tests:\n===============")

    try:
        test_bmssp_tiny()
        print("BMSSP Tiny Test: PASS")
    except AssertionError:
        print("BMSSP Tiny Test: FAIL")

    try:
        test_bmssp_no_destination()
        print("BMSSP Test without destination: PASS")
    except AssertionError:
        print("BMSSP Test without destination: FAIL")

    try:
        test_bmssp_with_destination()
        print("BMSSP Test with destination: PASS")
    except AssertionError:
        print("BMSSP Test with destination: FAIL")

    try:
        test_bmssp_zero_weight()
        print("BMSSP Zero-Weight Test: PASS")
    except AssertionError:
        print("BMSSP Zero-Weight Test: FAIL")

    try:
        test_bmssp_zero_weight_2()
        print("BMSSP Zero-Weight 2 Test: PASS")
    except AssertionError:
        print("BMSSP Zero-Weight 2 Test: FAIL")
