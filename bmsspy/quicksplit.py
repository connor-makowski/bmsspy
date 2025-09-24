def median(arr:list[int|float]) -> int|float:
    """
    Function:

    - Calculates the median of a list of numbers by sorting the list and finding the middle value or the average of the two middle values.

    Requires:

    - arr: A list of integers or floats.

    Returns:

    - The median value as an integer or float.
    """
    len_arr = len(arr)
    idx = len_arr // 2
    sorted_arr = sorted(arr)
    if len_arr%2 == 1:
        return sorted_arr[idx]
    else:
        return (sorted_arr[idx - 1] + sorted_arr[idx]) / 2

def median_of_medians(arr:list[int|float], split_size:int=5) -> int|float:
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

    - split_size: The size of the sublists to create
        - Default is 5
        - Must be an odd number to ensure a single median value

    """
    split_median_idx = split_size // 2

    while True:
        len_arr = len(arr)
        if len_arr <= split_size:
            return median(arr)
        extra = []
        # Allow for arrays not divisible by split_size
        if len_arr % split_size != 0:
            extra = [median(arr[len_arr - (len_arr % split_size):])]
            arr = arr[:len_arr - (len_arr % split_size)]
        medians = [sorted(arr[i:i+split_size])[split_median_idx] for i in range(0, len(arr), split_size)]
        arr = medians + extra

def quicksplit(arr, lower_bucket_size:int=None):
    """
    Function:

    - Splits an array into two buckets using a variant of the Quickselect algorithm.

    Required Arguments:

    - arr: A list of integers or floats to be split.

    Optional Arguments:

    - lower_bucket_size: The desired size of the lower bucket.
        - If not provided, the function will split the array into two equal halves (or as close as possible).
    
    Returns:

    - A dictionary with two keys:
        - 'lower': A list containing the lower bucket of elements.
        - 'higher': A list containing the higher bucket of elements.
    """
    # If no lower bucket size is given, split in half or as close as possible
    if lower_bucket_size is None:
        lower_bucket_size = len(arr)//2
    higher = []
    lower = []
    while True:
        pivot = median_of_medians(arr)
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
            return {
                'lower': lower,
                'higher': higher
            }

def sortsplit(arr, lower_bucket_size:int=None):
    """
    Function:

    - Splits an array into two buckets by sorting the array and dividing it at a specified index.

    Required Arguments:

    - arr: A list of integers or floats to be split.

    Optional Arguments:

    - lower_bucket_size: The desired size of the lower bucket.
        - If not provided, the function will split the array into two equal halves (or as close as possible).
    
    Returns:

    - A dictionary with two keys:
        - 'lower': A list containing the lower bucket of elements.
        - 'higher': A list containing the higher bucket of elements.

    """
    if lower_bucket_size is None:
        lower_bucket_size = len(arr)//2
    sorted_arr = sorted(arr)
    return {
        'lower': sorted_arr[:lower_bucket_size],
        'higher': sorted_arr[lower_bucket_size:]
    }