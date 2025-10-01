import random

from bmsspy.data_structures.heap_data_structure import (
    BmsspDataStructure as BmsspDataStructureHeap,
)
from bmsspy.data_structures.data_structure import (
    BmsspDataStructure as BmsspDataStructureAlgo,
)
def basic_test():
    """
    Basic sanity test for BmsspDataStructure implementations.
    """
    ds = BmsspDataStructureAlgo(subset_size=3, upper_bound=100)
    assert ds.is_empty()

    ds.insert_key_value(1, 50)
    ds.insert_key_value(2, 30)
    ds.insert_key_value(3, 70)
    ds.insert_key_value(4, 20)
    ds.insert_key_value(5, 90)

    assert not ds.is_empty()

    remaining_best, subset = ds.pull()
    assert remaining_best == 70
    assert subset == {4, 2, 1}

    remaining_best, subset = ds.pull()
    assert remaining_best == 100
    assert subset == {3, 5}

    assert ds.is_empty()

    ds.insert_key_value(6, 10)
    remaining_best, subset = ds.pull()
    assert remaining_best == 100
    assert subset == {6}

    assert ds.is_empty()

def test_data_structure_parity(seed):
    """
    Verify that both BmsspDataStructure implementations behave identically.
    """
    random.seed(seed)

    subset_size = random.randint(1, 10)
    upper_bound = random.randint(100, 2000)

    ds_heap = BmsspDataStructureHeap(subset_size, upper_bound)
    ds_algo = BmsspDataStructureAlgo(subset_size, upper_bound)
    key_values = {}
    # Test insert_key_value
    for _ in range(100):
        key = random.randint(0, 100)
        value = random.randint(upper_bound // 2, upper_bound - 1)
        if key in key_values:
            if value < key_values[key]:
                key_values[key] = value
        else:
            key_values[key] = value
        ds_heap.insert_key_value(key, value)
        ds_algo.insert_key_value(key, value)

    assert not ds_heap.is_empty()
    assert not ds_algo.is_empty()

    # Test pull
    remaining_best_heap, subset_heap = ds_heap.pull()
    remaining_best_algo, subset_algo = ds_algo.pull()
    assert remaining_best_heap == remaining_best_algo
    assert set(key_values[k] for k in subset_heap) == set(key_values[k] for k in subset_algo)

    # Test batch_prepend
    batch = []
    for _ in range(50):
        key = random.randint(101, 200)
        value = random.randint(0, upper_bound // 2 - 1)
        if key in key_values:
            if value < key_values[key]:
                key_values[key] = value
        else:
            key_values[key] = value
        batch.append((key, value))

    ds_heap.batch_prepend(set(batch))
    ds_algo.batch_prepend(batch)

    # Pull until empty
    while not ds_heap.is_empty() and not ds_algo.is_empty():
        remaining_best_heap, subset_heap = ds_heap.pull()
        remaining_best_algo, subset_algo = ds_algo.pull()
        assert remaining_best_heap == remaining_best_algo
        assert set(key_values[k] for k in subset_heap) == set(key_values[k] for k in subset_algo)

    assert ds_heap.is_empty()
    assert ds_algo.is_empty()


if __name__ == "__main__":
    print("\n===============\nData structure Tests:\n===============")
    basic_test()
    for i in range(10000):
        test_data_structure_parity(i)
    print("All tests passed!")
