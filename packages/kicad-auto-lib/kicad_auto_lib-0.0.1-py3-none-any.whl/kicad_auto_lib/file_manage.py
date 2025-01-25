"""
file_manage.py - A module for managing files and folders within a KiCad library system.

This module provides a set of utilities to manage KiCad project files, including symbol,
footprint, and 3D model files. It ensures that the necessary directory structures are in
place, handles file operations such as moving and deleting files, and integrates with
version control systems like Git for committing changes.

The module is designed to be used in conjunction with a KiCad project, where it helps
maintain the organization and consistency of library components. It adheres to PEP 8
standards and best practices for readability, maintainability, and clarity.

Functions
---------
projectfolder_lib_table_check_and_create()
    Ensures that KiCad project-specific symbol and footprint files exist, creating them if necessary.

libfolder_scan_for_libs()
    Scans the top-level directories in the libraries root path and returns a list of existing libraries.

libfolder_create_structure_if_needed(folder_name: str)
    Ensures that the specified library folder has the required subfolder structure.

lib_root_folder_path_build() -> Path
    Constructs and returns the path to the root folder of the library system.

lib_folder_path_build(lib_name: str) -> Path
    Constructs and returns the path to a specific library folder.

lib_symbol_folder_path_build(lib_name: str) -> Path
    Constructs and returns the path to the symbol folder within a specific library.

lib_footprint_folder_path_build(lib_name: str) -> Path
    Constructs and returns the path to the footprint folder within a specific library.

lib_3dmodel_folder_path_build(lib_name: str) -> Path
    Constructs and returns the path to the 3D model folder within a specific library.

user_prompt_library(lib_list: List[str], file: str) -> str
    Prompts the user to select a library from a list by entering a corresponding number.

lib_move_file(folder_to_copy_to: Path, file_to_move: Path) -> Optional[Path]
    Moves a file to a specified folder, handling retries and overwrite prompts.

lib_delete_file(file_to_delete: Path) -> Optional[bool]
    Deletes a file, handling retries and error messages.

add_to_lib(file_path: Path, file: Path)
    Adds a KiCad file (symbol, footprint, or 3D model) to the specified library.

projectfolder_search_for_symbols_and_footprints(directory: str)
    Traverses a directory and processes KiCad files with specific extensions.

libfolder_check_and_init() -> List[str]
    Scans for libraries and ensures they have the required subfolder structure.

Notes
-----
- The module assumes that the environment is properly set up with the necessary constants and variables.
- The module integrates with external utilities for reading and writing S-expressions and managing Git repositories.
"""

import os
from typing import List, Optional
from pathlib import Path
import shutil
import time

from .variables import lib_list_read
from .constants import (
    PROJECT_ROOT_PATH,
    LIBRARIES_ROOT_PATH,
    KICAD_CUSTOM_SYMBOL_FILE,
    KICAD_CUSTOM_FOOTPRINT_FILE,
    KICAD_CUSTOM_SYMBOL_FILE_DEFAULT_CONTENT,
    KICAD_CUSTOM_FOOTPRINT_FILE_DEFAULT_CONTENT,
    LIBRARY_SYMBOL_NAME,
    LIBRARY_FOOTPRINT_FOLDER,
    LIBRARY_3DMODEL_FOLDER,
    KICAD_SYMBOL_EXT,
    KICAD_FOOTPRINT_EXT,
    KICAD_3DMODEL_EXT,
    KICAD_SYMBOL_LIB_DEFAULT_CONTENT
)
from . import Sexp_read_write as sexp_util
from . import git_manage as git


def projectfolder_lib_table_check_and_create():
    """
    Checks for the existence of KiCad project specific symbol and footprint files in the specified folder.
    If the files are missing, they are created with default content.

    Parameters
    ----------
    None

    Raises
    ------
    FileNotFoundError
        If the specified folder does not exist in the PROJECT_ROOT_PATH.
    """
    # Construct the full path to the folder
    folder_path = Path(PROJECT_ROOT_PATH)

    # Ensure the folder exists
    if not folder_path.exists():
        raise FileNotFoundError(f"The specified folder does not exist: {folder_path}")

    # Define the file paths
    symbol_file_path = folder_path / KICAD_CUSTOM_SYMBOL_FILE
    footprint_file_path = folder_path / KICAD_CUSTOM_FOOTPRINT_FILE

    # Create the symbol file if it doesn't exist
    if not symbol_file_path.exists():
        with open(symbol_file_path, 'w') as symbol_file:
            symbol_file.write(KICAD_CUSTOM_SYMBOL_FILE_DEFAULT_CONTENT)
        print(f"Created KiCad project specific symbol file: {symbol_file_path}")

    # Create the footprint file if it doesn't exist
    if not footprint_file_path.exists():
        with open(footprint_file_path, 'w') as footprint_file:
            footprint_file.write(KICAD_CUSTOM_FOOTPRINT_FILE_DEFAULT_CONTENT)
        print(f"Created KiCad project specific footprint file: {footprint_file_path}")


def libfolder_scan_for_libs() -> List:
    """
    Scans the top-level directories in the LIBRARIES_ROOT_PATH and returns a list of folders,
    excluding hidden folders (e.g., .git).

    Returns
    -------
    list
        A list of folder names (strings) present at the top level of LIBRARIES_ROOT_PATH,
        excluding hidden folders.
    """
    # Convert the LIBRARIES_ROOT_PATH to a Path object for OS-independent operations
    root_path = Path(LIBRARIES_ROOT_PATH)

    # Ensure the root path exists
    if not root_path.exists():
        raise FileNotFoundError(f"The specified path does not exist: {root_path}")

    # Get all top-level directories in the root path, excluding hidden folders
    folders = [
        entry.name for entry in root_path.iterdir()
        if entry.is_dir() and not entry.name.startswith('.')
    ]

    return folders


def libfolder_create_structure_if_needed(folder_name):
    """
    Ensures that the specified folder has the required subfolders (LIBRARY_FOOTPRINT_FOLDER and LIBRARY_3DMODEL_FOLDER).
    If the subfolders do not exist, they are created.

    Parameters
    ----------
    folder_name : str
        The name of the folder (must be a top-level folder in LIBRARIES_ROOT_PATH).

    Raises
    ------
    FileNotFoundError
        If the specified folder does not exist in the LIBRARIES_ROOT_PATH.
    """
    # Construct the full path to the folder
    folder_path = Path(LIBRARIES_ROOT_PATH) / folder_name

    # Ensure the folder exists
    if not folder_path.exists():
        raise FileNotFoundError(f"The specified folder does not exist: {folder_path}")

    # Define the required subfolders
    required_folders = [LIBRARY_FOOTPRINT_FOLDER, LIBRARY_3DMODEL_FOLDER]

    # Create the required subfolders if they don't exist
    for required_folder in required_folders:
        subfolder_path = folder_path / required_folder
        if not subfolder_path.exists():
            subfolder_path.mkdir(parents=True, exist_ok=True)
            print(f"Initializing new library folder: {subfolder_path}")

    # Create an empty symbol library file
    symbol_lib_path = folder_path / LIBRARY_SYMBOL_NAME
    if not symbol_lib_path.exists():
        with open(symbol_lib_path, 'w') as symbol_file:
            symbol_file.write(KICAD_SYMBOL_LIB_DEFAULT_CONTENT)
        print(f"Initializing empty symbol library: {symbol_lib_path}")

        # if add_to_lib_tables:
            # Check and create KiCad custom symbol and footprint files
            

        


##% Utilities

def lib_root_folder_path_build() -> Path:
    return Path(PROJECT_ROOT_PATH) / Path(LIBRARIES_ROOT_PATH)

def lib_folder_path_build(lib_name: str) -> Path:
    return Path(PROJECT_ROOT_PATH) / Path(LIBRARIES_ROOT_PATH) / Path(lib_name)


def lib_symbol_folder_path_build(lib_name: str) -> Path:
    return Path(PROJECT_ROOT_PATH) / Path(LIBRARIES_ROOT_PATH) / Path(lib_name) / Path(LIBRARY_SYMBOL_NAME)

def lib_footprint_folder_path_build(lib_name: str) -> Path:
    return Path(PROJECT_ROOT_PATH) / Path(LIBRARIES_ROOT_PATH) / Path(lib_name) / Path(LIBRARY_FOOTPRINT_FOLDER)

def lib_3dmodel_folder_path_build(lib_name: str) -> Path:
    return Path(PROJECT_ROOT_PATH) / Path(LIBRARIES_ROOT_PATH) / Path(lib_name) / Path(LIBRARY_3DMODEL_FOLDER)

def user_prompt_library(lib_list: List[str], file: str) -> str:
    """
    Prompt the user to select an item from a list by entering a corresponding number.

    Parameters
    ----------
    lib_list : List[str]
        A list of items from which the user will select.

    Returns
    -------
    str
        The selected item from the list.

    Raises
    ------
    ValueError
        If the list is empty.
    """

    # Display the list with corresponding numbers starting from 1
    print(f"\nCopy {file} to:\n")
    for index, item in enumerate(lib_list, start=1):
        print(f"{index}. {item}")

    while True:
        try:
            # Prompt the user for input
            user_input = input("Enter the number corresponding to your choice: ")
            
            # Convert the input to an integer
            choice = int(user_input)
            
            # Check if the choice is within the valid range
            if 1 <= choice <= len(lib_list):
                return lib_list[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(lib_list)}.")
        
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def lib_move_file(folder_to_copy_to: Path, file_to_move: Path) -> Optional[Path]:
    """
    Move a file to a specified folder, retrying every 5 seconds for up to 10 times if the move fails.
    Prompts the user to overwrite if the file already exists at the destination.

    Parameters
    ----------
    folder_to_copy_to : Path
        The destination folder where the file should be moved.
    file_to_move : Path
        The file to be moved.

    Returns
    -------
    Optional[Path]
        The path to the moved file if successful, None otherwise.

    Raises
    ------
    FileNotFoundError
        If the file_to_move does not exist.
    NotADirectoryError
        If the folder_to_copy_to is not a directory.
    """
    
    # Check if the file exists
    if not file_to_move.exists():
        raise FileNotFoundError(f"The file {file_to_move} does not exist.")

    # Check if the destination is a directory
    if not folder_to_copy_to.is_dir():
        raise NotADirectoryError(f"The path {folder_to_copy_to} is not a directory.")

    # Determine the destination path
    destination_path = folder_to_copy_to / file_to_move.name

    # Check if the file already exists at the destination
    if destination_path.exists():
        # Prompt the user to confirm overwrite
        overwrite = input(f"The file {destination_path} already exists in this library. Overwrite? (y/[any]): ")
        if overwrite.lower() != 'y':
            print("Operation aborted: File already exists and will not be overwritten.")
            return None

    # Retry mechanism
    max_retries = 10
    retry_delay = 5  # in seconds

    for attempt in range(max_retries):
        try:
            # Attempt to move the file
            shutil.move(str(file_to_move), str(destination_path))
            print(f"File successfully moved to {destination_path}")
            # Waiting because of redetection after deleting a file (unknown reason!)
            time.sleep(1)
            return destination_path
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Operation failed.")
                return None


def lib_delete_file(file_to_delete: Path) -> Optional[bool]:
    """
    Delete a file, retrying every 5 seconds for up to 10 times if the deletion fails.

    Parameters
    ----------
    file_to_delete : Path
        The file to be deleted.

    Returns
    -------
    Optional[bool]
        True if the file was successfully deleted, False if the operation failed.
        Returns None if the file does not exist.

    Raises
    ------
    FileNotFoundError
        If the file_to_delete does not exist.
    """
    
    # Check if the file exists
    if not file_to_delete.exists():
        print(f"The file {file_to_delete} does not exist.")
        return None

    # Retry mechanism
    max_retries = 10
    retry_delay = 5  # in seconds

    for attempt in range(max_retries):
        try:
            # Attempt to delete the file
            os.remove(file_to_delete)
            print(f"File successfully deleted: {file_to_delete}")
            # Waiting because of redetection after deleting a file (unknown reason!)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Operation failed.")
                return False

def add_to_lib(file_path: Path, file: Path):
    """
    Add a KiCad file (symbol, footprint, or 3D model) to the specified library.

    This function reads the list of available libraries, prompts the user to select a library
    (if multiple are available), and then performs the necessary operations to add the file
    to the selected library. The function handles different file types (symbols, footprints,
    3D models) appropriately by merging, moving, or modifying the files as needed.

    Parameters
    ----------
    file_path : Path
        The path to the KiCad file to be added to the library.

    file : Path
        The file name (including extension) of the KiCad file.

    Notes
    -----
    - The function assumes that the library list is already set up and accessible.
    - The function performs specific operations based on the file type:
        - For `.kicad_sym` files, it merges the symbol into the library.
        - For `.kicad_mod` files, it moves the footprint to the library and updates the 3D model path.
        - For `.step` or `.stp` files, it moves the 3D model to the library.

    Raises
    ------
    None
        The function handles errors internally by printing messages to the console and returning early.

    """
    lib_list = lib_list_read()
    if not lib_list:
        print("Error: please create a subfolder in your library folder first.") 
        return

    # Default 
    lib_to_copy_to = lib_list[0]

    if len(lib_list)>1:
        lib_to_copy_to = user_prompt_library(lib_list, file)


    if file.endswith(KICAD_SYMBOL_EXT):

        print(f"Will merge {file} to {lib_to_copy_to}")
        # Get Content
        sexp_file = sexp_util.file_Sexp_load(file_path)
        if not sexp_file:
            print("Error reading file")
            return
        # Modify Footprint field
        updated_sexp = sexp_util.symbollib_edit_footprints(sexp_file, lib_to_copy_to)
        # Add to symbol library
        sexp_file_lib = sexp_util.file_Sexp_load(lib_symbol_folder_path_build(lib_to_copy_to))
        merged_sexp = sexp_util.symbollib_merge_new_with_lib(updated_sexp, sexp_file_lib)
        sexp_util.file_Sexp_save(lib_symbol_folder_path_build(lib_to_copy_to), merged_sexp)
        # Remove old file
        lib_delete_file(file_path)



    elif file.endswith(KICAD_FOOTPRINT_EXT):
        # Get folder to move to
        folder_to_copy_to = lib_footprint_folder_path_build(lib_to_copy_to)
        print(f"Will copy {file} to {folder_to_copy_to}")
        # Move file
        lib_new_path = lib_move_file(folder_to_copy_to, file_path)
        if not lib_new_path:
            print("Error moving the file, please delete and try again")
            return
        # Modify model value
        sexp_file = sexp_util.file_Sexp_load(lib_new_path)
        updated_sexp = sexp_util.footprintlib_edit_3dmodel_path(sexp_file, lib_3dmodel_folder_path_build(lib_to_copy_to))
        sexp_util.file_Sexp_save(lib_new_path, updated_sexp)

    
    elif file.endswith(KICAD_3DMODEL_EXT):
        # Get folder to move to
        folder_to_copy_to = lib_3dmodel_folder_path_build(lib_to_copy_to)
        # Move file
        print(f"Will copy {file} to {folder_to_copy_to}")
        # Move file
        lib_new_path = lib_move_file(folder_to_copy_to, file_path)
        if not lib_new_path:
            print("Error moving the file, please delete and try again")
            return

    # Once successful, commit and push on git.

    
    if git.git_check_if_repo(lib_folder_path_build(lib_to_copy_to)):
        print("Pushing to repo")
        commit_mess = f"{file} added"
        git.git_commit_and_push(lib_folder_path_build(lib_to_copy_to), commit_mess)
        

    if git.git_check_if_repo(lib_root_folder_path_build()):
        print("Pushing to repo")
        commit_mess = f"{file} added to {lib_to_copy_to}"
        git.git_commit_and_push(lib_root_folder_path_build(), commit_mess)
        

# For initial search only
def projectfolder_search_for_symbols_and_footprints(directory: str):
    """
    Traverse a directory and process KiCad files with specific extensions.

    This function walks through the directory structure, identifies files with
    `.kicad_sym`, `.kicad_mod`, or `.step` extensions, and processes them.

    Parameters
    ----------
    directory : Path
        The root directory to start traversing.
    """
    for root, _, files in os.walk(Path(directory)):
        for file in files:
            if file.endswith(KICAD_SYMBOL_EXT) or file.endswith(KICAD_FOOTPRINT_EXT) or file.endswith(KICAD_3DMODEL_EXT):
                file_path = Path(os.path.join(root, file))
                # print(file_path)
                add_to_lib(file_path, file)
                print(f"{file} added")
                

            # if file.endswith(KICAD_SYMBOL_EXT):
            #     file_path = os.path.join(root, file)
            #     new_symbol_lib_found(file_path)



            # if file.endswith(KICAD_FOOTPRINT_EXT):
            #     file_path = os.path.join(root, file)
            #     # new_footprint_found
            #     # Edit 3D model

            
            # if file.endswith(KICAD_3DMODEL_EXT):
            #     file_path = os.path.join(root, file)
            #     # Mode to right folder



def libfolder_check_and_init() -> List:
    #To run before every add and at launch
# Scan for top-level folders
    folders = libfolder_scan_for_libs()
    print("Libraries:", folders)

    # Ensure required subfolders exist for each folder
    for folder in folders:
        libfolder_create_structure_if_needed(folder)

    return folders
        


# if __name__ == "__main__":
#     # """
#     # Test 1 for prompt
#     # """
#     # library = ["Python", "JavaScript", "C++", "Java", "Go"]
#     # selected_language = user_prompt_library(library, "hello")
#     # print(f"You selected: {selected_language}")

#     projectfolder_search_for_symbols_and_footprints(PROJECT_ROOT_PATH)