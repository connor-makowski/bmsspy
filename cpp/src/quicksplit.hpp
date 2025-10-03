#ifndef QUICKSPLIT_HPP
#define QUICKSPLIT_HPP

#include <vector>
#include <map>

struct QuickSplitResult {
    std::vector<double> lower;
    std::vector<double> higher;
    double pivot;
};

struct QuickSplitDictResult {
    std::map<int, double> lower;
    std::map<int, double> higher;
    double pivot;
};

double median(std::vector<double> arr, bool split = true);

double median_of_medians(std::vector<double> arr, int split_size = 5, bool split = true);

QuickSplitResult quicksplit(std::vector<double> arr, int lower_bucket_size = -1);

QuickSplitDictResult quicksplit_dict(const std::map<int, double>& data, int lower_bucket_size = -1);

#endif // QUICKSPLIT_HPP