cmake_minimum_required(VERSION 3.14)
project(spanning_tree_cpp)

# -----------------------------
# Set C++ standard
# -----------------------------
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# -----------------------------
# Find Packages
# -----------------------------
find_package(Python COMPONENTS Interpreter Development REQUIRED)

# -----------------------------
# Add nanobind
# -----------------------------
include(FetchContent)
FetchContent_Declare(
    nanobind
    GIT_REPOSITORY https://github.com/wjakob/nanobind.git
    GIT_TAG v2.9.2  # Specify the version you want
    GIT_SHALLOW TRUE  # Only fetch the specific commit, faster download
)
FetchContent_MakeAvailable(nanobind)

# -----------------------------
# CASTRO BMSSP module
# -----------------------------
nanobind_add_module(castro_cpp
    bindings/castro_bindings.cpp
    src/castro.hpp
)