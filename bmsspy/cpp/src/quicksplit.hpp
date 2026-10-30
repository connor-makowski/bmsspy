#pragma once

#include <vector>
#include <cmath>
#include <algorithm>
#include <stdexcept>
#include <utility>

namespace bmsspy {

template <typename ValType = double>
inline ValType median(std::vector<ValType> arr, bool split = true) {
    size_t len_arr = arr.size();
    if (len_arr == 0) return ValType(0);
    size_t idx = len_arr / 2;
    std::sort(arr.begin(), arr.end());
    if (len_arr % 2 == 1) {
        return arr[idx];
    } else if (split) {
        return (arr[idx - 1] + arr[idx]) / ValType(2);
    } else {
        return arr[idx - 1];
    }
}

template <typename ValType = double>
inline ValType median_of_medians(std::vector<ValType> arr, size_t split_size = 5, bool split = true) {
    size_t split_median_idx = split_size / 2;

    while (true) {
        size_t len_arr = arr.size();
        if (len_arr <= split_size) {
            return median<ValType>(arr, split);
        }
        std::vector<ValType> extra;
        if (len_arr % split_size != 0) {
            size_t rem = len_arr % split_size;
            std::vector<ValType> rem_arr(arr.end() - rem, arr.end());
            extra.push_back(median<ValType>(rem_arr, split));
            arr.resize(len_arr - rem);
        }
        std::vector<ValType> medians;
        medians.reserve(arr.size() / split_size + 1);
        for (size_t i = 0; i < arr.size(); i += split_size) {
            std::vector<ValType> sub(arr.begin() + i, arr.begin() + i + split_size);
            std::sort(sub.begin(), sub.end());
            medians.push_back(sub[split_median_idx]);
        }
        medians.insert(medians.end(), extra.begin(), extra.end());
        arr = std::move(medians);
    }
}

template <typename ValType = double>
struct QuicksplitResult {
    std::vector<ValType> lower;
    std::vector<ValType> higher;
    ValType pivot;
};

template <typename ValType = double>
inline QuicksplitResult<ValType> quicksplit(std::vector<ValType> arr, int lower_bucket_size = -1) {
    size_t n = arr.size();
    if (n == 0) return {{}, {}, ValType(0)};
    size_t target_size;
    if (lower_bucket_size <= 0) {
        target_size = (n + 1) / 2;
    } else {
        target_size = static_cast<size_t>(lower_bucket_size);
    }

    std::vector<ValType> higher;
    std::vector<ValType> lower;

    while (true) {
        ValType pivot = median_of_medians<ValType>(arr, 5, false);
        std::vector<ValType> below;
        std::vector<ValType> pivots;
        std::vector<ValType> above;

        for (ValType x : arr) {
            if (x < pivot) below.push_back(x);
            else if (x > pivot) above.push_back(x);
            else pivots.push_back(x);
        }

        size_t count_below = below.size() + lower.size();
        if (target_size < count_below) {
            higher.insert(higher.begin(), above.begin(), above.end());
            higher.insert(higher.begin(), pivots.begin(), pivots.end());
            arr = std::move(below);
        } else if (target_size > count_below + pivots.size()) {
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.end());
            arr = std::move(above);
        } else {
            size_t pivot_split_idx = target_size - count_below;
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.begin() + pivot_split_idx);

            std::vector<ValType> rem_pivots(pivots.begin() + pivot_split_idx, pivots.end());
            rem_pivots.insert(rem_pivots.end(), above.begin(), above.end());
            rem_pivots.insert(rem_pivots.end(), higher.begin(), higher.end());
            higher = std::move(rem_pivots);

            if (pivot_split_idx == 0 && !below.empty()) {
                pivot = *std::max_element(below.begin(), below.end());
            }
            return {lower, higher, pivot};
        }
    }
}

template <typename KeyType, typename ValType = double>
struct QuicksplitTupleResult {
    std::vector<std::pair<KeyType, ValType>> lower;
    std::vector<std::pair<KeyType, ValType>> higher;
    ValType pivot;
};

template <typename KeyType, typename ValType = double>
inline QuicksplitTupleResult<KeyType, ValType> quicksplit_tuple(
    std::vector<std::pair<KeyType, ValType>> data,
    int lower_bucket_size = -1
) {
    size_t n = data.size();
    if (n == 0) return {{}, {}, ValType(0)};
    size_t target_size;
    if (lower_bucket_size <= 0) {
        target_size = (n + 1) / 2;
    } else {
        target_size = static_cast<size_t>(lower_bucket_size);
    }

    std::vector<std::pair<KeyType, ValType>> higher;
    std::vector<std::pair<KeyType, ValType>> lower;
    std::vector<std::pair<KeyType, ValType>> arr = std::move(data);

    while (true) {
        std::vector<ValType> vals;
        vals.reserve(arr.size());
        for (const auto& p : arr) vals.push_back(p.second);

        ValType pivot = median_of_medians<ValType>(vals, 5, false);
        std::vector<std::pair<KeyType, ValType>> below;
        std::vector<std::pair<KeyType, ValType>> pivots;
        std::vector<std::pair<KeyType, ValType>> above;

        for (const auto& item : arr) {
            if (item.second < pivot) below.push_back(item);
            else if (item.second > pivot) above.push_back(item);
            else pivots.push_back(item);
        }

        size_t count_below = below.size() + lower.size();
        if (target_size < count_below) {
            higher.insert(higher.begin(), above.begin(), above.end());
            higher.insert(higher.begin(), pivots.begin(), pivots.end());
            arr = std::move(below);
        } else if (target_size > count_below + pivots.size()) {
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.end());
            arr = std::move(above);
        } else {
            size_t pivot_split_idx = target_size - count_below;
            lower.insert(lower.end(), below.begin(), below.end());
            lower.insert(lower.end(), pivots.begin(), pivots.begin() + pivot_split_idx);

            std::vector<std::pair<KeyType, ValType>> rem_pivots(pivots.begin() + pivot_split_idx, pivots.end());
            rem_pivots.insert(rem_pivots.end(), above.begin(), above.end());
            rem_pivots.insert(rem_pivots.end(), higher.begin(), higher.end());
            higher = std::move(rem_pivots);

            if (pivot_split_idx == 0 && !below.empty()) {
                ValType max_b = below[0].second;
                for (const auto& item : below) {
                    if (item.second > max_b) max_b = item.second;
                }
                pivot = max_b;
            }
            return {lower, higher, pivot};
        }
    }
}

} // namespace bmsspy
