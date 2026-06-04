# Local Imports
from bmsspy.helpers.fast import FastSet, FastDict, FastLookup

print("\n===============\nFast Data Structure Tests:\n===============")

try:
    fs = FastSet(10)
    fs.add(1)
    fs.add(3)
    fs.add(5)
    assert str(fs) == "FastSet({1,3,5})", f"FastSet str failed: {str(fs)}"
    print("FastSet: __str__ Test Passed")
except Exception as e:
    print(f"FastSet: __str__ Test Failed: {e}")

try:
    fd = FastDict(10)
    fd[1] = 100
    fd[3] = 300
    assert str(fd) == "FastDict({1: 100, 3: 300})", f"FastDict str failed: {str(fd)}"
    print("FastDict: __str__ Test Passed")
except Exception as e:
    print(f"FastDict: __str__ Test Failed: {e}")

try:
    fl = FastLookup(10)
    fl[1] = 100
    fl[3] = 300
    assert str(fl).startswith("FastLookup Object @"), f"FastLookup str failed: {str(fl)}"
    print("FastLookup: __str__ Test Passed")
except Exception as e:
    print(f"FastLookup: __str__ Test Failed: {e}")
