"""
Sexp_read_write.py - Edit S-expressions files (like Kicad libs)

This module provides functionalities for reading, writing, and manipulating KiCad library files using S-expressions.
It includes utilities for handling both symbol and footprint libraries, as well as functions for modifying and merging
these libraries. The module also supports retry mechanisms for file operations to handle transient errors.

Functions:
- libtable_uri_symbol_build(name: str) -> str: Constructs the URI for a symbol library.
- libtable_uri_footprint_build(name: str) -> str: Constructs the URI for a footprint library.
- file_Sexp_load(filepath: str) -> Optional[List]: Loads a KiCad library from a file.
- file_Sexp_save(filepath: str, sexp_file: List) -> Optional[bool]: Saves a KiCad library to a file.
- symbollib_edit_footprints(sexp_file: List, new_prefix: str) -> List: Modifies the 'Footprint' properties in the S-expression.
- symbollib_merge_new_with_lib(sexp_file_to_merge: List, sexp_file_lib: List) -> List: Merges two KiCad symbol libraries.
- file_footprint_update(sexp_list: List, new_footprint: str, symbol_index: int = 0) -> Optional[List]: Updates the 'Footprint' property of a specific symbol.
- footprintlib_edit_3dmodel_path(sexp_file: List, new_path: str) -> List: Modifies the 3D model path in a KiCad footprint.
- libtable_generate_entry(name: str, uri: str) -> List: Generates a library table entry.
- libtable_add_library(library_table_sexp: List, new_entry: List) -> List: Adds a new library entry to the library table.
- libtable_compare_entries(current_sexp: List, lib_name_list: List[str]) -> Optional[List[str]]: Checks for missing library names in the library table.
- libtable_check_missing_entries(lib_list: List) -> None: Adds missing library entries to the library table.
- main(): Main function for testing the module functionalities.

The module adheres to PEP 8 standards and includes extensive docstrings and comments for clarity and maintainability.
"""
import os
import time
from typing import List, Optional
from pathlib import Path
import sexpdata as sexp



from . constants import (KICAD_LIBRARY_TEMPLATE_ENTRY, 
KICAD_CUSTOM_SYMBOL_FILE, 
KICAD_CUSTOM_FOOTPRINT_FILE,
KICAD_PROJECT_ROOT_PATH,
LIBRARIES_ROOT_PATH,
LIBRARY_FOOTPRINT_FOLDER,
LIBRARY_SYMBOL_NAME
)


##% File utilities 

def libtable_uri_symbol_build(name: str) -> str:
    
    path = Path(KICAD_PROJECT_ROOT_PATH) / Path(LIBRARIES_ROOT_PATH) / Path(name) / Path(LIBRARY_SYMBOL_NAME)
    return path.as_posix()

def libtable_uri_footprint_build(name: str) -> str:
    
    path = Path(KICAD_PROJECT_ROOT_PATH) / Path(LIBRARIES_ROOT_PATH) / Path(name) / Path(LIBRARY_FOOTPRINT_FOLDER)
    return path.as_posix()

#%% Loading and Saving
import time
from typing import List, Optional
from pathlib import Path

def file_Sexp_load(filepath: str) -> Optional[List]:
    """
    Load a KiCad library from a file, retrying every 5 seconds for up to 10 times if the load
    operation fails.

    Parameters
    ----------
    filepath : str
        The path to the file containing the KiCad symbol library.

    Returns
    -------
    Optional[List]
        The loaded S-expression data representing the KiCad symbol library if successful, None otherwise.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    
    # Convert filepath to a Path object for easier handling
    file_path = Path(filepath)

    # Check if the file exists
    if not file_path.exists():
        # raise FileNotFoundError(f"The file {file_path} does not exist.")
        return

    # Retry mechanism
    max_retries = 10
    retry_delay = 5  # in seconds

    for attempt in range(max_retries):
        try:
            # Attempt to load the file
            with open(file_path, 'r') as file:
                return sexp.loads(file.read())
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Operation failed.")
                return None



def file_Sexp_save(filepath: str, sexp_file: List) -> Optional[bool]:
    """
    Save the updated KiCad library back to a file, retrying every 5 seconds for up to 10 times
    if the save operation fails.

    Parameters
    ----------
    filepath : str
        The path to the file where the updated KiCad library will be saved.
    sexp_file : List
        The updated S-expression data representing the KiCad library.

    Returns
    -------
    Optional[bool]
        True if the file was successfully saved, False if the operation failed.
        Returns None if the operation was aborted by the user.

    Raises
    ------
    FileNotFoundError
        If the directory of the filepath does not exist.
    """
    
    # Convert filepath to a Path object for easier handling
    file_path = Path(filepath)

    # Check if the directory exists
    if not file_path.parent.exists():
        raise FileNotFoundError(f"The directory {file_path.parent} does not exist.")

      # Retry mechanism
    max_retries = 10
    retry_delay = 5  # in seconds

    for attempt in range(max_retries):
        try:
            # Attempt to save the file
            with open(file_path, 'w') as file:
                file.write(sexp.dumps(sexp_file, pretty_print=True))
            print(f"File successfully saved to {file_path}.")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Operation failed.")
                return False



def symbollib_edit_footprints(sexp_file: List, new_prefix: str)  -> List:
    """
    Modify the 'Footprint' properties in the S-expression by replacing the prefix.

    Parameters
    ----------
    sexp_file : list
        The S-expression data representing the KiCad symbol library.
    new_prefix : str
        The new prefix to replace the 'xxx' part in the 'Footprint' property.

    Returns
    -------
    List
        The modified S-expression with updated 'Footprint' properties.
    """
    for element in sexp_file:
        if isinstance(element, list) and len(element) > 0:
            if isinstance(element[0], sexp.Symbol) and element[0].value() == 'symbol':
                for sub_element in element:
                    if isinstance(sub_element, list) and len(sub_element) > 0:
                        if isinstance(sub_element[0], sexp.Symbol) and sub_element[0].value() == 'property':
                            if sub_element[1] == 'Footprint':
                                # Edit the 'Footprint' property
                                footprint_parts = sub_element[2].split(':')
                                if len(footprint_parts) >= 2:
                                    new_footprint = f"{new_prefix}:{footprint_parts[1]}"
                                    sub_element[2] = new_footprint
    return sexp_file

def symbollib_merge_new_with_lib(sexp_file_to_merge: List, sexp_file_lib: List) -> List:
    """
    Merge two KiCad symbol library S-expressions at the symbol level.

    Parameters
    ----------
    sexp_file_to_merge : list
        The S-expression data representing the new symbols to be merged.
    sexp_file_lib : list
        The S-expression data representing the existing symbol library.

    Returns
    -------
    List
        The merged S-expression containing symbols from both files.
    """
    # Iterate through `sexp_file_to_merge` to find and extract symbols
    for element in sexp_file_to_merge:
        if isinstance(element, list) and len(element) > 0:
            if isinstance(element[0], sexp.Symbol) and element[0].value() == 'symbol':
                # Append the symbol to `sexp_file_lib`
                sexp_file_lib.append(element)
    
    return sexp_file_lib

def file_footprint_update(sexp_list: List, new_footprint: str, symbol_index: int = 0) -> Optional[List]:
    """
    Update the 'Footprint' property of a specific symbol in the S-expression data.

    Parameters
    ----------
    sexp_list : list
        The S-expression data representing the KiCad symbol library.
    new_footprint : str
        The new value for the 'Footprint' property.
    symbol_index : int
        The index of the symbol to update (default is 0).

    Returns
    -------
    Optional[List]
        The updated S-expression data with the modified 'Footprint' property,
        or None if the symbol index is invalid.
    """
    symbols = [element for element in sexp_list if isinstance(element, list) and len(element) > 0 and isinstance(element[0], sexp.Symbol) and element[0].value() == 'symbol']
    if symbol_index >= len(symbols):
        print(f"Error: Invalid symbol index {symbol_index}. There are only {len(symbols)} symbols.")
        return None

    target_symbol = symbols[symbol_index]
    for sub_element in target_symbol:
        if isinstance(sub_element, list) and len(sub_element) > 0:
            if isinstance(sub_element[0], sexp.Symbol) and sub_element[0].value() == 'property':
                if sub_element[1] == 'Footprint':
                    sub_element[2] = new_footprint
                    print(f"Updated footprint for symbol '{target_symbol[1]}' to '{new_footprint}'.")
                    return sexp_list
    return sexp_list

def footprintlib_edit_3dmodel_path(sexp_file: List, new_path: str) -> List:
    """
    Modify the 3D model path in a KiCad footprint S-expression.

    Parameters
    ----------
    sexp_file : List
        The S-expression data representing the KiCad footprint.
    new_path : str
        The new path to use for the 3D model, without the filename.

    Returns
    -------
    List
        The modified S-expression with the updated 3D model path.

    Notes
    -----
    The function assumes that the `model` variable exists in the S-expression.
    If not, the function will return the original S-expression unchanged.
    """
    for element in sexp_file:
        if isinstance(element, list) and len(element) > 0:
            if isinstance(element[0], sexp.Symbol) and element[0].value() == 'model':
                # Extract the current model path
                current_model_path = element[1]
                # Extract the filename from the current path
                filename = os.path.basename(current_model_path.replace('\\', '/'))
                # Compose the new path with the filename
                new_model_path = os.path.join(new_path, filename).replace('\\', '/')
                # Update the model path in the S-expression
                element[1] = new_model_path
                return sexp_file
    return sexp_file

def libtable_generate_entry(name: str, uri: str) -> List:
    """
    Generate a library table entry by editing the KICAD_LIBRARY_TEMPLATE_ENTRY.

    Parameters
    ----------
    name : str
        The library name to insert into the template.
    uri : str
        The library URI to insert into the template.

    Returns
    -------
    List
        The edited S-expression representing the library table entry.
    """
    # Parse the template S-expression
    lib_element = sexp.loads(KICAD_LIBRARY_TEMPLATE_ENTRY)

    # Ensure the element is a list starting with the 'lib' symbol
    if len(lib_element) > 0 and isinstance(lib_element[0], sexp.Symbol) and lib_element[0].value() == 'lib':
        # Traverse the properties of the 'lib' element
        for i, sub_element in enumerate(lib_element):

            if isinstance(sub_element[0], sexp.Symbol) and len(sub_element) >= 1 and sub_element[0].value() == 'name':
                # Update the 'name' property
                sub_element[1] = name
            elif isinstance(sub_element[0], sexp.Symbol) and len(sub_element) >= 1 and sub_element[0].value() == 'uri':
                # Update the 'uri' property
                sub_element[1] = uri

    return lib_element

def libtable_add_library(library_table_sexp: List, new_entry: List) -> List:
    """
    Add a new library entry to the library table (sym or fp) S-expression.

    Parameters
    ----------
    library_table_sexp : List
        The S-expression representing the KiCad library table.
    new_entry : List
        The new library entry to add.

    Returns
    -------
    List
        The updated S-expression with the new library entry added.
    """

    # print(library_table_sexp)
    # print(new_entry)

    library_table_sexp.append(new_entry)

    return library_table_sexp


# def libtable_create_entry(file: str, name: str, uri: str) -> None:
#     """
#     Add a library table entry to an existing KiCad library table file.

#     Parameters
#     ----------
#     file : str
#         The filepath of the KiCad library table to modify.
#     name : str
#         The library name to insert into the template.
#     uri : str
#         The library URI to insert into the template.
#     """
#     # Load the existing library table
#     library_table_sexp = file_Sexp_load(file)


#     # Generate the new library table entry
#     new_entry = libtable_generate_entry(name, uri)
#     print(new_entry)
#     # Add the new entry to the library table
#     updated_library_table_sexp = libtable_add_library(library_table_sexp, new_entry)
#     print(updated_library_table_sexp)

#     # Save the updated library table back to the file
#     file_Sexp_save(file, updated_library_table_sexp)

def libtable_compare_entries(current_sexp: List, lib_name_list: List[str]) -> Optional[List[str]]:
    """
    Check for library names in `lib_name_list` that are missing in the S-expression library table.

    Parameters
    ----------
    current_sexp : List
        The S-expression data representing the KiCad library table.
    lib_name_list : List[str]
        A list of library names to check against.

    Returns
    -------
    List[str]
        A list of library names in `lib_name_list` that are missing in the S-expression.
        Returns `lib_name_list` if no 'lib' entries are found in the S-expression.
    """
    # Extract all 'name' values from 'lib' entries in the S-expression
    lib_names_in_sexp = set()

    for element in current_sexp:
        if isinstance(element, list) and len(element) > 0:
            if isinstance(element[0], sexp.Symbol) and element[0].value() == 'lib':
                for sub_element in element:
                    if isinstance(sub_element, list) and len(sub_element) > 0:
                        if isinstance(sub_element[0], sexp.Symbol) and sub_element[0].value() == 'name':
                            lib_names_in_sexp.add(sub_element[1])

    # If no 'lib' entries are found, return the full `lib_name_list`
    if not lib_names_in_sexp:
        print("Warning: No 'lib' entries found in the S-expression.")
        return lib_name_list

    # Find names in `lib_name_list` that are missing in the S-expression
    missing_names = [
        name for name in lib_name_list if name not in lib_names_in_sexp
    ]

    return missing_names


def libtable_check_missing_entries(lib_list: List) -> None:
    """
    Add a library table entry to an existing KiCad library table file.

    Parameters
    ----------
 
    """
    # Load the existing library table
    sym_lib_table_sexp = file_Sexp_load(KICAD_CUSTOM_SYMBOL_FILE)

    new_libs = libtable_compare_entries (sym_lib_table_sexp, lib_list)
    # print(new_libs)
    if not new_libs:
        return
    
    print("Adding new libs")
    fp_lib_table_sexp = file_Sexp_load(KICAD_CUSTOM_FOOTPRINT_FILE)

    for lib_name in new_libs:

        # Load the existing library table


        lib_symbol_uri = libtable_uri_symbol_build(lib_name)
        lib_footprint_uri = libtable_uri_footprint_build(lib_name)
        print(lib_symbol_uri)

                # Generate the new library table entry
        new_symbol_entry = libtable_generate_entry(lib_name, lib_symbol_uri)
        new_footprint_entry = libtable_generate_entry(lib_name, lib_footprint_uri)
        print(new_symbol_entry)
        # Add the new entry to the library table
        sym_lib_table_sexp = libtable_add_library(sym_lib_table_sexp, new_symbol_entry)
        fp_lib_table_sexp = libtable_add_library(fp_lib_table_sexp, new_footprint_entry)
        print(sym_lib_table_sexp)
        print(fp_lib_table_sexp)

        # Save the updated library table back to the file
    file_Sexp_save(KICAD_CUSTOM_SYMBOL_FILE, sym_lib_table_sexp)
    file_Sexp_save(KICAD_CUSTOM_FOOTPRINT_FILE, fp_lib_table_sexp)

    # # Generate the new library table entry
    # new_entry = libtable_generate_entry(name, uri)
    # print(new_entry)
    # # Add the new entry to the library table
    # updated_library_table_sexp = libtable_add_library(library_table_sexp, new_entry)
    # print(updated_library_table_sexp)

    # # Save the updated library table back to the file
    # file_Sexp_save(file, updated_library_table_sexp)

# def main():
#     """
#     Test 1 - TBD
#     Main function to load a KiCad symbol library, list symbols and footprints,
#     update a specific symbol's footprint, and save the changes.
#     """
#     filepath = '../_Libraries/StepUp_Custom/symbols2.kicad_sym'  # Replace with your actual file path
#     filepath2 = '../_Libraries/StepUp_Custom/symbols.kicad_sym'  # Replace with your actual file path
#     filepath3 = '../_Libraries/StepUp_Custom/symbols.kicad_sym'  # Replace with your actual file path
#     lib_name = 'mylibname'  # Replace with your new footprint value

#     # Load the KiCad symbol library
#     sexp_file = file_Sexp_load(filepath)
#     print("File loaded successfully.")

#     # List all symbols and their footprints
#     updated_sexp = symbollib_edit_footprints(sexp_file, lib_name)
#     # for idx, (symbol_name, footprint) in enumerate(symbols_with_footprints):
#     #     print(f"Symbol {idx}: '{symbol_name}' has footprint '{footprint}'.")

#     # Update the 'Footprint' property (default is the first symbol, index 0)
#     # updated_sexp = file_footprint_update(sexp_file, new_footprint, symbol_index=0)
#     print(updated_sexp)
#     sexp_file_lib = file_Sexp_load(filepath2)
#     merged_sexp = symbollib_merge_new_with_lib(updated_sexp, sexp_file_lib)

#     # # Save the updated KiCad symbol library
#     file_Sexp_save(filepath3, merged_sexp)

#     """
#     Test 2 -TBD
#     """

#     # lib_list = ['MyCustomLibrary',  "testLib", "test", "rr12Te"]

#     # # Add a new entry to the library table
#     # libtable_check_missing_entries(lib_list)

#     """
#     Test 3 - Footprint editing of 3d models
#     """
#     filepath = '../_Libraries/StepUp_Custom/footprints.pretty/RF-SMD_MM8030-2610RK0.kicad_mod'  # Replace with your actual file path
#     filepath2 = '../_Libraries/StepUp_Custom/footprints.pretty/RF-SMD_edit.kicad_mod'  # Replace with your actual file path
#     lib_name = 'mylibname'  # Replace with your new footprint value

#     # Load the KiCad symbol library
#     sexp_file = file_Sexp_load(filepath)
#         # Define the new path
#     new_path = "../newpath"
    
#     # Edit the 3D model path
#     updated_sexp = footprintlib_edit_3dmodel_path(sexp_file, new_path)

#     file_Sexp_save(filepath2, updated_sexp)

# if __name__ == "__main__":
#     main()