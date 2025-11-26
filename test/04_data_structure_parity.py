# General Imports
import random

# Local Imports
from bmsspy.data_structures.heap_data_structure import BmsspHeapDataStructure
from bmsspy.data_structures.data_structure import BmsspDataStructure
from bmsspy.data_structures.unique_data_structure import (
    UniqueBmsspDataStructure,
)
from bmsspy.data_structures.list_data_structure import ListBmsspDataStructure


def basic_test(ds_class):
    """
    Basic sanity test for BmsspDataStructure implementations.
    """
    ds = ds_class(
        subset_size=3,
        upper_bound=100,
        recursion_data_id=1,
        recursion_data_list=[0] * 10,
    )
    assert ds.is_empty()

    ds.insert_key_value(1, 50)
    ds.insert_key_value(2, 30)
    ds.insert_key_value(3, 70)
    ds.insert_key_value(4, 20)
    ds.insert_key_value(5, 90)

    assert not ds.is_empty()

    remaining_best, subset = ds.pull()
    assert remaining_best == 70
    assert set(subset) == {4, 2, 1} and len(subset) == 3

    remaining_best, subset = ds.pull()
    assert remaining_best == 100
    assert set(subset) == {3, 5} and len(subset) == 2

    assert ds.is_empty()

    ds.insert_key_value(6, 10)
    remaining_best, subset = ds.pull()
    assert remaining_best == 100
    assert set(subset) == {6} and len(subset) == 1

    assert ds.is_empty()


def test_data_structure_parity(seed, ds_class_1, ds_class_2):
    """
    Verify that both BmsspDataStructure implementations behave identically.
    """
    random.seed(seed)

    subset_size = random.randint(1, 10)
    upper_bound = random.randint(300, 2000)

    ds_class_1_obj = ds_class_1(
        subset_size,
        upper_bound,
        recursion_data_id=1,
        recursion_data_list=[0] * 201,
    )
    ds_class_2_obj = ds_class_2(
        subset_size,
        upper_bound,
        recursion_data_id=1,
        recursion_data_list=[0] * 201,
    )
    key_values = {}
    used_values = set()
    # Test insert_key_value
    for _ in range(100):
        key = random.randint(0, 100)
        value = random.randint(upper_bound // 2, upper_bound - 1)
        while value in used_values:
            value = random.randint(upper_bound // 2, upper_bound - 1)
        used_values.add(value)
        if key in key_values:
            if value < key_values[key]:
                key_values[key] = value
        else:
            key_values[key] = value
        ds_class_1_obj.insert_key_value(key, value)
        ds_class_2_obj.insert_key_value(key, value)

    assert not ds_class_1_obj.is_empty()
    assert not ds_class_2_obj.is_empty()

    # Test pull
    remaining_best_ds_1, subset_ds_1 = ds_class_1_obj.pull()
    remaining_best_ds_2, subset_ds_2 = ds_class_2_obj.pull()
    assert remaining_best_ds_1 == remaining_best_ds_2
    assert set(key_values[k] for k in subset_ds_1) == set(
        key_values[k] for k in subset_ds_2
    )

    # Test batch_prepend
    batch = []
    for _ in range(50):
        key = random.randint(101, 200)
        while key in key_values:
            key = random.randint(101, 200)
        value = random.randint(0, upper_bound // 2 - 1)
        while value in used_values:
            value = random.randint(0, upper_bound // 2 - 1)
        used_values.add(value)
        if key in key_values:
            if value < key_values[key]:
                key_values[key] = value
        else:
            key_values[key] = value
        batch.append((key, value))

    ds_class_1_obj.batch_prepend(set(batch))
    ds_class_2_obj.batch_prepend(batch)

    # Pull until empty
    while not ds_class_1_obj.is_empty() and not ds_class_2_obj.is_empty():
        remaining_best_ds_1, subset_ds_1 = ds_class_1_obj.pull()
        remaining_best_ds_2, subset_ds_2 = ds_class_2_obj.pull()
        assert remaining_best_ds_1 == remaining_best_ds_2
        assert set(key_values[k] for k in subset_ds_1) == set(
            key_values[k] for k in subset_ds_2
        )

    assert ds_class_1_obj.is_empty()
    assert ds_class_2_obj.is_empty()


if __name__ == "__main__":
    print("\n===============\nData structure Tests:\n===============")
    basic_test(BmsspDataStructure)
    basic_test(BmsspHeapDataStructure)
    basic_test(UniqueBmsspDataStructure)
    basic_test(ListBmsspDataStructure)
    for i in range(10000):
        # First test parity between non-unique data structures
        test_data_structure_parity(
            i, BmsspDataStructure, BmsspHeapDataStructure
        )
        # Then test parity between unique and non-unique data structures - essentially ensuring our tests are valid
        test_data_structure_parity(
            i, BmsspHeapDataStructure, UniqueBmsspDataStructure
        )
        # Finally test parity between unique and list data structures
        test_data_structure_parity(
            i, UniqueBmsspDataStructure, ListBmsspDataStructure
        )
    print("Data Structure tests passed!")
