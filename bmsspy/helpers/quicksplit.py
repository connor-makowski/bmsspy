from math import ceil
from typing import Any

def median(arr:list[int|float], split:bool=True) -> int|float:
    """
    Function:

    - Calculates the median of a list of numbers by sorting the list and finding the middle value or the average of the two middle values.

    Required Arguments:

    - arr: A list of integers or floats.

    Optional Arguments:

    - split: A boolean indicating weather to calculate a split if the list length is even
        - Default is True
        - If True, the median is the average of the two middle values for even-length lists
        - If False, the median is the lower of the two middle values for even-length lists
        - If False, this ensures that the returned median is always an element of the original list

    Returns:

    - The median value as an integer or float.
    """
    len_arr = len(arr)
    idx = len_arr // 2
    sorted_arr = sorted(arr)
    if len_arr%2 == 1:
        return sorted_arr[idx]
    elif split:   
        return (sorted_arr[idx - 1] + sorted_arr[idx]) / 2
    else:
        return sorted_arr[idx - 1]

def median_of_medians(arr:list[int|float], split_size:int=5, split:bool=True) -> int|float:
    """
    Function:

    - Computes the median of medians of a list of numbers. 
    - This is done by dividing the list into sublists of a fixed size (5 in this case)
        - For each sublist, find the median of each sublist
        - Then iteratively find the median of those medians
        - Stop when the list is smaller than or equal to the split size and return the median of that list

    Required Arguments:

    - arr: A list of integers or floats.

    Optional Arguments:

    - split: A boolean indicating weather to calculate a split value if the final iterated length is even
        - Default is True
        - If True, the median is the average of the two middle values for even-length lists
        - If False, the median is the lower of the two middle values for even-length lists
        - If False, this ensures that the returned median is always an element of the original list

    Optional Arguments:

    - split_size: The size of the sublists to create
        - Default is 5
        - Must be an odd number to ensure a single median value

    """
    split_median_idx = split_size // 2

    while True:
        len_arr = len(arr)
        if len_arr <= split_size:
            return median(arr, split=split)
        extra = []
        # Allow for arrays not divisible by split_size
        if len_arr % split_size != 0:
            extra = [median(arr[len_arr - (len_arr % split_size):])]
            arr = arr[:len_arr - (len_arr % split_size)]
        medians = [sorted(arr[i:i+split_size])[split_median_idx] for i in range(0, len(arr), split_size)]
        arr = medians + extra

def quicksplit(arr:list[int|float], lower_bucket_size:int=None) -> dict:
    """
    Function:

    - Splits an array into two buckets using a variant of the Quickselect algorithm.

    Required Arguments:

    - arr: A list of integers or floats to be split.

    Optional Arguments:

    - lower_bucket_size: The desired size of the lower bucket.
        - If not provided, the function will split the array into two equal halves (or as close as possible).
    
    Returns:

    - A dictionary with three keys:
        - 'lower': A list containing the lower bucket of elements.
        - 'higher': A list containing the higher bucket of elements.
        - 'pivot': The max value in the lower bucket or None if the lower bucket is empty (i.e., lower_bucket_size is 0).
    """
    # If no lower bucket size is given, split in half or as close as possible
    if lower_bucket_size is None:
        lower_bucket_size = len(arr)/2
    lower_bucket_size = ceil(lower_bucket_size)
    assert 0 < lower_bucket_size <= len(arr), "lower_bucket_size must be positive and less than or equal to the length of the array"
    higher = []
    lower = []
    while True:
        pivot = median_of_medians(arr, split=False)
        # Loop over the array once to partition into three lists
        # This is faster than using list 3 list comprehensions
        below = []
        pivots = []
        above = []
        for x in arr:
            if x < pivot:
                below.append(x)
            elif x > pivot:
                above.append(x)
            else:
                pivots.append(x)

        count_below = len(below) + len(lower)
        if lower_bucket_size < count_below:
            higher = pivots + above + higher
            arr = below
        elif lower_bucket_size > count_below + len(pivots):
            lower = lower + below + pivots
            arr = above
        else:
            pivot_split_idx = lower_bucket_size - count_below
            lower = lower + below + pivots[:pivot_split_idx]
            higher = pivots[pivot_split_idx:] + above + higher
            if pivot_split_idx == 0:
                pivot = max(below)
            return {
                'lower': lower,
                'higher': higher,
                'pivot': pivot
            }

def quicksplit_dict(data:dict[Any, list[int|float]], lower_bucket_size:int=None) -> dict:
    """
    Function:

    - Splits a dictionary of values into two dicts using a variant of the Quickselect algorithm.

    Required Arguments:

    - data: A dictionary where keys are any hashable type and values are lists of integers or floats to be split.

    Optional Arguments:

    - lower_bucket_size: The desired size of the lower bucket.
        - If not provided, the function will split the array into two equal halves (or as close as possible).
    
    Returns:

    - A dictionary with three keys:
        - 'lower': A dict of the lower bucket of elements.
        - 'higher': A dict of the higher bucket of elements.
        - 'pivot': The max value in the lower bucket or None if the lower bucket is empty (i.e., lower_bucket_size is 0).
    """
    # If no lower bucket size is given, split in half or as close as possible
    if lower_bucket_size is None:
        lower_bucket_size = len(data)/2
    lower_bucket_size = ceil(lower_bucket_size)
    assert 0 < lower_bucket_size <= len(data), "lower_bucket_size must be positive and less than or equal to the length of the array"
    higher = []
    lower = []
    arr = data.items()
    while True:
        pivot = median_of_medians([v for k, v in arr], split=False)
        # Loop over the array once to partition into three lists
        # This is faster than using list 3 list comprehensions
        below = []
        pivots = []
        above = []
        for item in arr:
            if item[1] < pivot:
                below.append(item)
            elif item[1] > pivot:
                above.append(item)
            else:
                pivots.append(item)

        count_below = len(below) + len(lower)
        if lower_bucket_size < count_below:
            higher = pivots + above + higher
            arr = below
        elif lower_bucket_size > count_below + len(pivots):
            lower = lower + below + pivots
            arr = above
        else:
            pivot_split_idx = lower_bucket_size - count_below
            lower = lower + below + pivots[:pivot_split_idx]
            higher = pivots[pivot_split_idx:] + above + higher
            if pivot_split_idx == 0:
                pivot = max([i[1] for i in below])
            return {
                'lower': dict(lower),
                'higher': dict(higher),
                'pivot': pivot
            }

def sortsplit(arr, lower_bucket_size:int=None) -> dict:
    """
    Function:

    - Splits an array into two buckets by sorting the array and dividing it at a specified index.

    Required Arguments:

    - arr: A list of integers or floats to be split.

    Optional Arguments:

    - lower_bucket_size: The desired size of the lower bucket.
        - If not provided, the function will split the array into two equal halves (or as close as possible).
    
    Returns:

    - A dictionary with three keys:
        - 'lower': A list containing the lower bucket of elements.
        - 'higher': A list containing the higher bucket of elements.
        - 'pivot': The max value in the lower bucket.

    """
    if lower_bucket_size is None:
        lower_bucket_size = len(arr)//2
    assert lower_bucket_size <= len(arr), "lower_bucket_size must be less than or equal to the length of the array"
    sorted_arr = sorted(arr)
    return {
        'lower': sorted_arr[:lower_bucket_size],
        'higher': sorted_arr[lower_bucket_size:],
        'pivot': sorted_arr[lower_bucket_size - 1] if lower_bucket_size > 0 else None
    }