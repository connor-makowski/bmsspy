from bmsspy.helpers.rbtree import RBTree

print("\n===============\nRed Black Tree Basic Tests:\n===============")

try:
    from bmsspy.bin.rbtree_cpp import RBTree_double_str
    test_list = [('RBTree', RBTree), ('RBTreeCpp', RBTree_double_str)]
except ImportError:
    test_list = [('RBTree', RBTree)]
    print("C++ RBTree bindings not available, skipping C++ tests.")

for class_name, class_obj in test_list:
    tree = class_obj()
    try:
        assert len(tree) == 0, "Empty tree length is not 0"
        tree.insert(10.0, "ten")
        tree.insert(20.0, "twenty")
        tree.insert(15.0, "fifteen")
        tree.insert(25.0, "twenty five")
        assert len(tree) == 4, "Tree length after insertions is not correct"
        assert tree.find(15.0).key == 15.0, "Exact find failed"
        assert tree.find(17.0, target="upper").key == 20.0, "Upper find failed"
        assert tree.find(17.0, target="lower").key == 15.0, "Lower find failed"
        tree.remove(20.0)
        assert len(tree) == 3, "Tree length after removal is not correct"
        assert tree.find(20.0) == None, "Find after removal failed"
        assert tree.find(5.0, target="lower") == None, "Lower find at min failed"
        assert tree.find(30.0, target="upper") == None, "Upper find at max failed"
        print(f"{class_name}: Basic Tests Passed")
    except Exception as e:
        print(f"{class_name}: Basic Tests Failed: {e}")

print("\n===============\nRed Black Tree Performance Tests:\n===============")

# Performance test
import time
import random


for class_name, class_obj in test_list:
    print(f"\n{class_name} Performance Tests:\n")
    for num_elements in [100, 1_000, 10_000, 100_000]:
        random.seed(42)
        elements = random.sample(range(num_elements * 10), num_elements)
        elements = [float(el) for el in elements]
        iterative_elements = elements[:-10]

        missing_elements = [
            random.randint(0, num_elements * 10) + 0.5 for _ in range(10)
        ]

        final_elements = elements[-10:]
        tree = class_obj()

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

        print(f"    {class_name} Time per Operation (n={num_elements}):")
        print(f"        Insert: {time_per_insert*1e6:.2f} µs")
        print(f"        Search: {time_per_search*1e6:.2f} µs")
        print(f"        Lower Search: {time_per_lower_search*1e6:.2f} µs")
        print(f"        Upper Search: {time_per_upper_search*1e6:.2f} µs")
        print(f"        Delete: {time_per_delete*1e6:.2f} µs")
