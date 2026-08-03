from bmsspy.helpers.fast import FastSet, FastDict, FastLookup


def test_fast_set():
    fs = FastSet(10)
    fs.add(1)
    fs.add(3)
    fs.add(5)
    assert str(fs) == "FastSet({1,3,5})"


def test_fast_dict():
    fd = FastDict(10)
    fd[1] = 100
    fd[3] = 300
    assert str(fd) == "FastDict({1: 100, 3: 300})"


def test_fast_lookup():
    fl = FastLookup(10)
    fl[1] = 100
    fl[3] = 300
    assert str(fl).startswith("FastLookup Object @")


if __name__ == "__main__":
    print("\n===============\nFast Data Structure Tests:\n===============")
    try:
        test_fast_set()
        print("FastSet: __str__ Test Passed")
    except Exception as e:
        print(f"FastSet: __str__ Test Failed: {e}")

    try:
        test_fast_dict()
        print("FastDict: __str__ Test Passed")
    except Exception as e:
        print(f"FastDict: __str__ Test Failed: {e}")

    try:
        test_fast_lookup()
        print("FastLookup: __str__ Test Passed")
    except Exception as e:
        print(f"FastLookup: __str__ Test Failed: {e}")
