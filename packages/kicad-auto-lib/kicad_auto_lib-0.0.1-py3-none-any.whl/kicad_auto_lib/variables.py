from typing import List


ALL_LIBS: List = []

def lib_list_read() -> List:
    """
    Access the global variable and return its value.

    Returns
    -------
    int
        The value of the global variable.
    """
    return ALL_LIBS


def lib_list_write(new_value: List) -> None:
    """
    Modify the global variable.

    Parameters
    ----------
    new_value : int
        The new value to assign to the global variable.
    """
    global ALL_LIBS
    ALL_LIBS = new_value