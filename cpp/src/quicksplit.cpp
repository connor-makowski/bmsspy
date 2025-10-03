#include "quicksplit.hpp"  // include header for declarations

#include <vector>
#include <algorithm>
#include <stdexcept>
#include <cmath>
#include <map>
#include <limits>

float median(std::vector<float> arr, bool split) {
    size_t len = arr.size();
    if (len == 0) throw std::invalid_argument("Cannot find median of empty array");

    std::sort(arr.begin(), arr.end());
    size_t idx = len / 2;

    if (len % 2 == 1) {
        return arr[idx];
    } else {
        if (split) {
            return (arr[idx - 1] + arr[idx]) / 2.0f;
        } else {
            return arr[idx - 1];
        }
    }
}

float median_of_medians(std::vector<float> arr, int split_size, bool split) {
    if (split_size % 2 == 0) {
        throw std::invalid_argument("split_size must be an odd number");
    }

    int split_median_idx = split_size / 2;

    while (true) {
        size_t len = arr.size();
        if (len <= static_cast<size_t>(split_size)) {
            return median(arr, split);
        }

        std::vector<float> medians;
        std::vector<float> extra;

        if (len % split_size != 0) {
            std::vector<float> tail(arr.end() - (len % split_size), arr.end());
            extra.push_back(median(tail));
            arr.resize(len - (len % split_size));
        }

        for (size_t i = 0; i < arr.size(); i += split_size) {
            std::vector<float> chunk(arr.begin() + i, arr.begin() + i + split_size);
            std::sort(chunk.begin(), chunk.end());
            medians.push_back(chunk[split_median_idx]);
        }

        arr = medians;
        arr.insert(arr.end(), extra.begin(), extra.end());
    }
}

QuickSplitResult quicksplit(std::vector<float> arr, int lower_bucket_size) {
    if (lower_bucket_size == -1) {
        lower_bucket_size = static_cast<int>(std::ceil(arr.size() / 2.0));
    }

    if (lower_bucket_size <= 0 || static_cast<size_t>(lower_bucket_size) > arr.size()) {
        throw std::invalid_argument("lower_bucket_size must be > 0 and <= arr size");
    }

    std::vector<float> lower, higher;

    while (true) {
        float pivot = median_of_medians(arr, 5, false);

        std::vector<float> below, above, pivots;
        for (float x : arr) {
            if (x < pivot)
                below.push_back(x);
            else if (x > pivot)
                above.push_back(x);
            else
                pivots.push_back(x);
        }

        int count_below = static_cast<int>(below.size() + lower.size());

        if (lower_bucket_size < count_below) {
            higher.insert(higher.end(), pivots.begin(), pivots.end());
            higher.insert(higher.end(), above.begin(), above.end());
            arr = below;
        } else if (lower_bucket_size > count_below + static_cast<int>(pivots.size())) {
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.end());
            arr = above;
        } else {
            int pivot_split_idx = lower_bucket_size - count_below;
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.begin() + pivot_split_idx);
            higher.insert(higher.end(), pivots.begin() + pivot_split_idx, pivots.end());
            higher.insert(higher.end(), above.begin(), above.end());

            float final_pivot;
            if (pivot_split_idx == 0 && !below.empty()) {
                final_pivot = *std::max_element(below.begin(), below.end());
            } else {
                final_pivot = pivot;
            }

            return {lower, higher, final_pivot};
        }
    }
}

QuickSplitDictResult quicksplit_dict(const std::map<int, float>& data, int lower_bucket_size) {
    if (lower_bucket_size == -1) {
        lower_bucket_size = static_cast<int>(std::ceil(data.size() / 2.0));
    }

    if (lower_bucket_size <= 0 || static_cast<size_t>(lower_bucket_size) > data.size()) {
        throw std::invalid_argument("lower_bucket_size must be > 0 and <= data size");
    }

    using Pair = std::pair<int, float>;
    std::vector<Pair> lower, higher;
    std::vector<Pair> arr(data.begin(), data.end());

    while (true) {
        std::vector<float> values;
        for (const auto& [key, val] : arr) {
            values.push_back(val);
        }

        float pivot = median_of_medians(values, 5, false);

        std::vector<Pair> below, above, pivots;
        for (const auto& item : arr) {
            if (item.second < pivot)
                below.push_back(item);
            else if (item.second > pivot)
                above.push_back(item);
            else
                pivots.push_back(item);
        }

        int count_below = static_cast<int>(below.size() + lower.size());

        if (lower_bucket_size < count_below) {
            higher.insert(higher.end(), pivots.begin(), pivots.end());
            higher.insert(higher.end(), above.begin(), above.end());
            arr = below;
        } else if (lower_bucket_size > count_below + static_cast<int>(pivots.size())) {
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.end());
            arr = above;
        } else {
            int pivot_split_idx = lower_bucket_size - count_below;
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.begin() + pivot_split_idx);
            higher.insert(higher.end(), pivots.begin() + pivot_split_idx, pivots.end());
            higher.insert(higher.end(), above.begin(), above.end());

            float final_pivot;
            if (pivot_split_idx == 0 && !below.empty()) {
                auto max_it = std::max_element(below.begin(), below.end(),
                    [](const Pair& a, const Pair& b) { return a.second < b.second; });
                final_pivot = max_it->second;
            } else {
                final_pivot = pivot;
            }

            std::map<int, float> lower_map, higher_map;
            for (const auto& item : lower) lower_map[item.first] = item.second;
            for (const auto& item : higher) higher_map[item.first] = item.second;

            return {lower_map, higher_map, final_pivot};
        }
    }
}
