try:
    from bmsspy._cpp import (
        Bmssp,
        BmsspC,
        reconstruct_path,
        median,
        median_of_medians,
        ListBmsspDataStructure,
        convert_to_constant_degree,
        convert_to_constant_out_degree,
    )
except ImportError:
    pass
