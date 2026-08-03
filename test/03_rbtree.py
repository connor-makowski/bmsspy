import random
from bmsspy.helpers.rbtree import RBTree


def test_rbtree_basic():
    tree = RBTree()
    assert len(tree) == 0
    tree.insert(10, "ten")
    tree.insert(20, "twenty")
    tree.insert(15, "fifteen")
    tree.insert(25, "twenty five")
    assert len(tree) == 4
    assert tree.find(15).key == 15
    assert tree.find(17, target="upper").key == 20
    assert tree.find(17, target="lower").key == 15
    tree.remove(20)
    assert len(tree) == 3
    assert tree.find(20) is None
    assert tree.find(5, target="lower") is None
    assert tree.find(30, target="upper") is None


def test_rbtree_performance():
    for num_elements in [100, 1_000, 10_000]:
        random.seed(42)
        elements = random.sample(range(num_elements * 10), num_elements)
        iterative_elements = elements[:-10]
        missing_elements = [
            random.randint(0, num_elements * 10) + 0.5 for _ in range(10)
        ]
        final_elements = elements[-10:]
        tree = RBTree()

        for el in iterative_elements:
            tree.insert(el, str(el))

        for el in final_elements:
            tree.insert(el, str(el))

        for el in final_elements:
            tree.find(el)

        for el in missing_elements:
            tree.find(el, target="lower")

        for el in missing_elements:
            tree.find(el, target="upper")

        for el in final_elements:
            tree.remove(el)


if __name__ == "__main__":
    print("\n===============\nRed Black Tree Tests:\n===============")
    try:
        test_rbtree_basic()
        print("RBTree: Basic Tests Passed")
    except Exception as e:
        print(f"RBTree: Basic Tests Failed: {e}")

    import time

    for num_elements in [100, 1_000, 10_000, 100_000]:
        random.seed(42)
        elements = random.sample(range(num_elements * 10), num_elements)
        iterative_elements = elements[:-10]
        missing_elements = [
            random.randint(0, num_elements * 10) + 0.5 for _ in range(10)
        ]
        final_elements = elements[-10:]
        tree = RBTree()

        for el in iterative_elements:
            tree.insert(el, str(el))

        start_time = time.perf_counter()
        for el in final_elements:
            tree.insert(el, str(el))
        end_time = time.perf_counter()
        time_per_insert = (end_time - start_time) / len(final_elements)

        start_time = time.perf_counter()
        for el in final_elements:
            tree.find(el)
        end_time = time.perf_counter()
        time_per_search = (end_time - start_time) / len(final_elements)

        start_time = time.perf_counter()
        for el in missing_elements:
            tree.find(el, target="lower")
        end_time = time.perf_counter()
        time_per_lower_search = (end_time - start_time) / len(missing_elements)

        start_time = time.perf_counter()
        for el in missing_elements:
            tree.find(el, target="upper")
        end_time = time.perf_counter()
        time_per_upper_search = (end_time - start_time) / len(missing_elements)

        start_time = time.perf_counter()
        for el in final_elements:
            tree.remove(el)
        end_time = time.perf_counter()
        time_per_delete = (end_time - start_time) / len(final_elements)

        print(f"RBTree Time per Operation (n={num_elements}):")
        print(f"    Insert: {time_per_insert*1e6:.2f} µs")
        print(f"    Search: {time_per_search*1e6:.2f} µs")
        print(f"    Lower Search: {time_per_lower_search*1e6:.2f} µs")
        print(f"    Upper Search: {time_per_upper_search*1e6:.2f} µs")
        print(f"    Delete: {time_per_delete*1e6:.2f} µs")
