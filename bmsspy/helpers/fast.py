class FastRoot:
    def __init__(self, size: int):
        # Happens in O(n) Time
        self.size = size
        self.scnt = 0
        self.memb = [0] * size
        self.clear()

    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return iter(self.data)
    
    def __contains__(self, key: int):
        return self.memb[key] == self.scnt
        
    def __repr__(self):
        return self.__str__()
    
    def __delitem__(self, key: int):
        # Does not happen in O(1) Time
        if self.memb[key] == self.scnt:
            self.memb[key] = -1
            self.data.remove(key)
        else:
            raise KeyError(key)
        return self
    
    def clear(self):
        self.scnt += 1
        self.data = []
        return self
    
    def invalidate(self, key: int):
        self.memb[key] = 0
        return self
    
    def __str__(self):
        return f"FastRoot({str(self.data)})"

class FastSet(FastRoot):
    def __str__(self):
        return f"FastSet({{{",".join(map(str, self.data))}}})"
    
    def __call__(self, data: list[int] | set[int] = list()):
        self.clear()
        self.extend(data)
        return self
    
    # Allow | operator for union
    def __or__(self, other: 'FastSet'):
        assert self.size == other.size, "FastSets must be of the same size to perform union"
        result = FastSet(self.size)()
        for key in self.data:
            result.add(key)
        for key in other.data:
            result.add(key)
        return result

    def add(self, key: int):
        if self.memb[key] != self.scnt:
            self.memb[key] = self.scnt
            self.data.append(key)
        return self

    def extend(self, items: list[int]):
        for item in items:
            if self.memb[item] != self.scnt:
                self.memb[item] = self.scnt
                self.data.append(item)
        return self
    
    def remove(self, key: int):
        return self.__delitem__(key)
    
    def update(self, other: set[int]):
        for key in other:
            if self.memb[key] != self.scnt:
                self.memb[key] = self.scnt
                self.data.append(key)
        return self

    
class FastDict(FastRoot):
    def __init__(self, size: int):
        super().__init__(size)
        self.vals = [0] * size

    def __str__(self):
        return f"FastDict({{{", ".join(f"{key}: {self.vals[key]}" for key in self.data)}}})"

    def __call__(self, data: dict[int, any] = dict()):
        self.clear()
        self.update(data)
        return self

    def __getitem__(self, key: int):
        if self.memb[key] != self.scnt:
            raise KeyError(key)
        return self.vals[key]
    
    def __setitem__(self, key: int, value):
        if self.memb[key] != self.scnt:
            self.memb[key] = self.scnt
            self.data.append(key)
        self.vals[key] = value
        return self
    
    #######################################
    # Allow cleanup
    #######################################
    def __delitem__(self, key: int):
        if self.memb[key] == self.scnt:
            self.memb[key] = 0
            self.vals[key] = 0
            self.data.remove(key)
        return self
    
    def invalidate(self, key: int):
        self.memb[key] = -1
        self.vals[key] = 0
        return self
    
    #######################################
    # Additional convenience methods to match dict interface
    #######################################
    def get(self, key: int, default=None):
        if self.memb[key] != self.scnt:
            return default
        return self.vals[key]
    
    def keys(self):
        for key in self.data:
            yield key

    def values(self):
        for key in self.data:
            yield self.vals[key]
        
    def items(self):
        for key in self.data:
            yield (key, self.vals[key])

    def update(self, other: dict[int, any]):
        for key, value in other.items():
            if self.memb[key] != self.scnt:
                self.memb[key] = self.scnt
                self.data.append(key)
            self.vals[key] = value
        return self
    
class FastLookup(FastRoot):
    def __init__(self, size: int):
        # The equivalent of a FastDict without storing active keys
        # This can be used to prevent memory bloat when you know the keys you will access beforehand
        # Does not support iteration over keys or values
        super().__init__(size)
        self.vals = [0] * size

    def __str__(self):
        return f"FastLookup Object @{self.__hash__()}"

    def __call__(self, data: dict[int, any] = dict()):
        self.clear()
        self.update(data)
        return self

    def __getitem__(self, key: int):
        if self.memb[key] != self.scnt:
            raise KeyError(key)
        return self.vals[key]
    
    def __setitem__(self, key: int, value):
        if self.memb[key] != self.scnt:
            self.memb[key] = self.scnt
        self.vals[key] = value
        return self
    
    def __iter__(self):
        raise NotImplementedError("FastLookup does not support iteration over keys or values.")
    
    #######################################
    # Allow cleanup
    #######################################
    def __delitem__(self, key: int):
        if self.memb[key] == self.scnt:
            self.memb[key] = -1
            self.vals[key] = 0
        return self
    
    def invalidate(self, key: int):
        self.memb[key] = -1
        self.vals[key] = 0
        return self
    
    #######################################
    # Additional convenience methods to match dict interface
    #######################################
    def get(self, key: int, default=None):
        if self.memb[key] != self.scnt:
            return default
        return self.vals[key]
    
    def update(self, other: dict[int, any]):
        if isinstance(other, FastLookup):
            raise TypeError("Cannot update FastLookup with another FastLookup")
        for key, value in other.items():
            if self.memb[key] != self.scnt:
                self.memb[key] = self.scnt
                self.data.append(key)
            self.vals[key] = value
        return self