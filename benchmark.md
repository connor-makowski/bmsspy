# BMSSP Benchmark Report

- **Date**: 2026-11-24 10:15:01
- **Runs per test**: 5 (after 1 warmup run)
- **Platform**: Linux x86_64 (Linux-7.0.0-43-generic-x86_64-with-glibc2.39)
- **Python Version**: 3.14.5
- **C++ Extension (`BmsspC`)**: Available (compiled)

## Summary Results

| Graph | Case / Style | Nodes | Edges | bmssp | bmssp_cd | bmssp_cpp | bmssp_cpp_cd |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Geograph Marnet | los_angeles | 11,062 | 34,698 | 209.8 ms | 773.5 ms | 14.5 ms | 46.5 ms |
| Geograph World Highways | los_angeles | 560,282 | 1,652,213 | 3.16 s | 8.30 s | 257.5 ms | 692.8 ms |
| GridGraph 50x50 | u5 (bltr) | 2,500 | 18,774 | 40.4 ms | 546.3 ms | 2.0 ms | 37.6 ms |
| GridGraph 50x50 | o5 (bltr) | 2,500 | 18,774 | 45.8 ms | 544.2 ms | 2.3 ms | 37.2 ms |
| GridGraph 100x100 | u5 (bltr) | 10,000 | 77,474 | 171.9 ms | 2.56 s | 7.7 ms | 158.8 ms |
| GridGraph 100x100 | o5 (bltr) | 10,000 | 77,474 | 170.8 ms | 2.36 s | 8.0 ms | 149.1 ms |

## Detailed Statistics

| Graph | Case | Algorithm | Mean | Min | Max | Stdev |
|---|---|---|---|---|---|---|
| Geograph Marnet | los_angeles | bmssp | 209.8 ms | 208.4 ms | 212.5 ms | 2.0 ms |
| Geograph Marnet | los_angeles | bmssp_cd | 773.5 ms | 710.1 ms | 869.4 ms | 82.2 ms |
| Geograph Marnet | los_angeles | bmssp_cpp | 14.5 ms | 14.5 ms | 14.6 ms | 0.02 ms |
| Geograph Marnet | los_angeles | bmssp_cpp_cd | 46.5 ms | 46.5 ms | 46.6 ms | 0.05 ms |
| Geograph World Highways | los_angeles | bmssp | 3.16 s | 3.03 s | 3.59 s | 239.9 ms |
| Geograph World Highways | los_angeles | bmssp_cd | 8.30 s | 7.23 s | 10.31 s | 1.46 s |
| Geograph World Highways | los_angeles | bmssp_cpp | 257.5 ms | 255.8 ms | 258.9 ms | 1.2 ms |
| Geograph World Highways | los_angeles | bmssp_cpp_cd | 692.8 ms | 690.3 ms | 694.8 ms | 1.9 ms |
| GridGraph 50x50 | u5 (bltr) | bmssp | 40.4 ms | 40.2 ms | 40.6 ms | 0.15 ms |
| GridGraph 50x50 | u5 (bltr) | bmssp_cd | 546.3 ms | 544.4 ms | 547.9 ms | 1.3 ms |
| GridGraph 50x50 | u5 (bltr) | bmssp_cpp | 2.0 ms | 1.9 ms | 2.0 ms | 0.02 ms |
| GridGraph 50x50 | u5 (bltr) | bmssp_cpp_cd | 37.6 ms | 37.5 ms | 37.7 ms | 0.09 ms |
| GridGraph 50x50 | o5 (bltr) | bmssp | 45.8 ms | 45.6 ms | 46.0 ms | 0.20 ms |
| GridGraph 50x50 | o5 (bltr) | bmssp_cd | 544.2 ms | 543.8 ms | 544.5 ms | 0.26 ms |
| GridGraph 50x50 | o5 (bltr) | bmssp_cpp | 2.3 ms | 2.2 ms | 2.3 ms | 0.03 ms |
| GridGraph 50x50 | o5 (bltr) | bmssp_cpp_cd | 37.2 ms | 37.2 ms | 37.3 ms | 0.05 ms |
| GridGraph 100x100 | u5 (bltr) | bmssp | 171.9 ms | 171.5 ms | 173.1 ms | 0.63 ms |
| GridGraph 100x100 | u5 (bltr) | bmssp_cd | 2.56 s | 2.42 s | 2.66 s | 122.2 ms |
| GridGraph 100x100 | u5 (bltr) | bmssp_cpp | 7.7 ms | 7.6 ms | 8.0 ms | 0.15 ms |
| GridGraph 100x100 | u5 (bltr) | bmssp_cpp_cd | 158.8 ms | 157.7 ms | 159.5 ms | 0.75 ms |
| GridGraph 100x100 | o5 (bltr) | bmssp | 170.8 ms | 170.4 ms | 171.6 ms | 0.48 ms |
| GridGraph 100x100 | o5 (bltr) | bmssp_cd | 2.36 s | 2.24 s | 2.44 s | 105.8 ms |
| GridGraph 100x100 | o5 (bltr) | bmssp_cpp | 8.0 ms | 8.0 ms | 8.0 ms | 0.02 ms |
| GridGraph 100x100 | o5 (bltr) | bmssp_cpp_cd | 149.1 ms | 148.2 ms | 150.3 ms | 0.90 ms |
