def median(arr:list[int|float]) -> int|float:
    len_arr = len(arr)
    idx = len_arr // 2
    sorted_arr = sorted(arr)
    if len_arr%2 == 1:
        return sorted_arr[idx]
    else:
        return (sorted_arr[idx - 1] + sorted_arr[idx]) / 2

def median_of_medians(arr:list[int|float]) -> int|float:
    split_size = 5 # Must be odd
    len_arr = len(arr)
    if len_arr <= split_size:
        return median(arr)
    extra = []
    # Allow for arrays not divisible by split_size
    if len_arr % split_size != 0:
        extra = [median(arr[len_arr - (len_arr % split_size):])]
        arr = arr[:len_arr - (len_arr % split_size)]
    medians = [sorted(arr[i:i+split_size])[split_size // 2] for i in range(0, len(arr), split_size)]
    return median_of_medians(medians + extra)

def quicksplit(arr, lower_bucket_size:int=None):
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
    if lower_bucket_size is None:
        lower_bucket_size = len(arr)//2
    sorted_arr = sorted(arr)
    return {
        'lower': sorted_arr[:lower_bucket_size],
        'higher': sorted_arr[lower_bucket_size:]
    }
        

# if __name__ == "__main__":       
#     import random
#     from pamda.pamda_timer import pamda_timer

#     random.seed(42)
#     tests = [
#         [random.random() for _ in range(10)],
#         [random.random() for _ in range(1_000)],
#         [random.random() for _ in range(1_000_000)],
#         [random.random() for _ in range(10_000_000)],
#     ]

#     for data in tests:
#         quicksplit_output = quicksplit(data)
#         sortsplit_output = sortsplit(data)

#         assert sorted(quicksplit_output['lower']) == sortsplit_output['lower'], f"Mismatch for Quickselect lower: {quicksplit_output['lower']} != {sortsplit_output['lower']}"
#         assert sorted(quicksplit_output['higher']) == sortsplit_output['higher'], f"Mismatch for Quickselect higher: {quicksplit_output['higher']} != {sortsplit_output['higher']}"

#         print(pamda_timer(quicksplit, iterations = 3).get_time_stats(arr=data, lower_bucket_size=len(data)//2))
#         print(pamda_timer(sortsplit, iterations = 3).get_time_stats(arr=data, lower_bucket_size=len(data)//2))