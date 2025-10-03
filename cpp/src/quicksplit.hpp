#ifndef QUICKSPLIT_HPP
#define QUICKSPLIT_HPP

#include <vector>
#include <map>

struct QuickSplitResult {
    std::vector<float> lower;
    std::vector<float> higher;
    float pivot;
};

struct QuickSplitDictResult {
    std::map<int, float> lower;
    std::map<int, float> higher;
    float pivot;
};

float median(std::vector<float> arr, bool split = true);

float median_of_medians(std::vector<float> arr, int split_size = 5, bool split = true);

QuickSplitResult quicksplit(std::vector<float> arr, int lower_bucket_size = -1);

QuickSplitDictResult quicksplit_dict(const std::map<int, float>& data, int lower_bucket_size = -1);

#endif // QUICKSPLIT_HPP