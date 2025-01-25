"""
kicad_auto_lib.py - Main script for automating KiCad library management.

This script serves as the entry point for the KiCad Auto Library management system. It initializes
the necessary library structures, performs an initial scan for existing KiCad files, and sets up
a directory monitoring system to handle new files added to the project directory. The script ensures
that all library components (symbols, footprints, and 3D models) are properly organized and managed.

The script integrates with other modules to handle file monitoring, directory scanning, and library
maintenance. It adheres to PEP 8 standards and best practices for readability, maintainability, and
clarity.

Functions
---------
main()
    The main function initializes the library system, performs an initial scan, and sets up directory
    monitoring. It handles the overall workflow of the KiCad Auto Library management system.

Notes
-----
- The script assumes that the environment is properly set up with the necessary constants, variables,
  and external modules (e.g., `file_monitor`, `file_manage`, `Sexp_read_write`).
- The script is designed to be executed as a standalone program. When run, it begins monitoring the
  specified project directory for new files and automatically organizes them into the appropriate
  library folders.
"""

from .constants import PROJECT_ROOT_PATH
from .variables import lib_list_read, lib_list_write
from .file_monitor import monitor_directory
from .file_manage import projectfolder_search_for_symbols_and_footprints, libfolder_check_and_init
from .Sexp_read_write import libtable_check_missing_entries


def main():
    """
    Main function to initiate the monitoring process.
    Sets the directory to monitor and calls the function to perform the task.

    Returns
    -------
    None
    """

    print("""
    Launching Kicad Auto Lib
    Maintained by chgayot @ StepUp Solutions
    """)

    all_libs = libfolder_check_and_init()
    lib_list_write(all_libs)
    libtable_check_missing_entries(lib_list_read())

    print("Launching initial scan")

    # Perform an initial scan of the directory
    print(f"Performing initial scan")

    projectfolder_search_for_symbols_and_footprints(PROJECT_ROOT_PATH)

    print(f"Listening for new lib files.")

    # Call the function to monitor the directory
    monitor_directory(PROJECT_ROOT_PATH)

if __name__ == "__main__":
    main()