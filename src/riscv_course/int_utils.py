import numpy as np

INT_TYPES: dict[str, np.number] = {
    "int64":  np.int64,
    "int32":  np.int32,
    "int16":  np.int16,
    "int8":   np.int8,
    "uint64": np.uint64,
    "uint32": np.uint32,
    "uint16": np.uint16,
    "uint8":  np.uint8
}

INT_TYPE_DESCRIPTION: dict[np.number, str] = {
    np.int64:  "64-х битное число со знаком",
    np.int32:  "32-х битное число со знаком",
    np.int16:  "16-ти битное число со знаком",
    np.int8:   "8-ми битное число со знаком",
    np.uint64: "64-х битное беззнаковое число",
    np.uint32: "32-х битное беззнаковое число",
    np.uint16: "16-ти битное беззнаковое число",
    np.uint8:  "8-ми битное беззнаковое число"
}

def get_ctype_name(type_name: str) -> str:
    return type_name + "_t"

def numpify_int_type(type_name: str, min_value: int | None, max_value: int | None) -> tuple[np.number, int, int]:
    numpy_type = INT_TYPES[type_name]

    info = np.iinfo(numpy_type)
    if min_value is None: min_value = info.min
    if max_value is None: max_value = info.max

    if min_value < info.min or min_value > info.max:
        raise ValueError(f"Invalid integer {min_value}. Expected number in range [{info.min}, {info.max}] for {numpy_type.__name__}")
    
    if max_value < info.min or max_value > info.max:
        raise ValueError(f"Invalid integer {min_value}. Expected number in range [{info.min}, {info.max}] for {numpy_type.__name__}")
    
    return numpy_type, min_value, max_value
