import os
import platform
import ctypes


def load_library():
    system = platform.system().lower()
    if system == "linux":
        lib_name = "libgnparser.so"
    elif system == "darwin":
        lib_name = "libgnparser.dylib"
    elif system == "windows":
        lib_name = "libgnparser.dll"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")
    lib_path = os.path.join(os.path.dirname(__file__), lib_name)
    return ctypes.CDLL(lib_path)


lib = load_library()
lib.ParseToString.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
lib.ParseToString.restype = ctypes.c_char_p
lib.FreeMemory.argtypes = [ctypes.c_char_p]
lib.FreeMemory.restype = None


def parse_to_string(name, fmt_str="compact", code_str=None, details=True, diaereses=True):
    result = lib.ParseToString(
        name.encode("utf-8"),
        fmt_str.encode("utf-8"),
        code_str.encode("utf-8") if code_str else None,
        details,
        diaereses
    )
    parsed = ctypes.string_at(result).decode("utf-8")
    lib.FreeMemory(result)
    return parsed
