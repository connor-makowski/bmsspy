import os

from bmsspy import BmsspC, has_cpp


def test_cpp_availability():
    require_cpp = os.environ.get("BMSSPY_REQUIRE_CPP") == "1"
    require_python = (
        os.environ.get("BMSSPY_REQUIRE_PYTHON") == "1"
        or os.environ.get("BMSSPY_SKIP_CPP") == "1"
    )
    assert not (
        require_cpp and require_python
    ), "Conflicting build expectations"
    if require_cpp:
        assert (
            has_cpp()
        ), "BMSSPY_REQUIRE_CPP=1 but the extension is unavailable"
        assert BmsspC.__module__ == "bmsspy.cpp"
    elif require_python:
        assert (
            not has_cpp()
        ), "Expected an installation without the C++ extension"
        assert BmsspC.__module__ == "bmsspy"


if __name__ == "__main__":
    test_cpp_availability()
