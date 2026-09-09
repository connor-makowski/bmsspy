try:
    from bmsspy._cpp import (
        Bmssp,
        BmsspC,
        reconstruct_path,
        median,
        median_of_medians,
        ListBmsspDataStructure,
    )
except ImportError:
    pass
