"""
file_monitor.py - Monitor and manage KiCad library files in a specified directory.

This module provides functionality to monitor a directory for changes in KiCad library files 
(e.g., `.kicad_sym`, `.kicad_mod`, `.3dshapes`) and perform necessary actions such as adding 
new files to the library and checking for missing entries in the library table.

The module utilizes the `watchdog` library to monitor file system events and triggers 
appropriate handlers when relevant files are created or modified.

Functions
---------
monitor_directory(path: str) -> None
    Monitor the specified directory for KiCad library files and manage them accordingly.

Classes
-------
KicadSymFileHandler
    Event handler class that triggers actions when KiCad library files are created or modified.

Constants
---------
KICAD_SYMBOL_EXT : str
    File extension for KiCad symbol files.
KICAD_FOOTPRINT_EXT : str
    File extension for KiCad footprint files.
KICAD_3DMODEL_EXT : str
    File extension for KiCad 3D model files.

Imports
-------
time : module
    Provides time-related functions.
os : module
    Provides a way of using operating system-dependent functionality.
pathlib.Path : class
    Represents filesystem paths.
watchdog.observers.Observer : class
    Observes file system events.
watchdog.events.FileSystemEventHandler : class
    Handles file system events.

External Dependencies
---------------------
constants : module
    Contains constants for file extensions.
file_manage : module
    Provides functions for managing library files.
Sexp_read_write : module
    Provides functions for reading and writing S-expressions.
variables : module
    Contains functions for reading and writing library lists.
"""

import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .constants import KICAD_SYMBOL_EXT, KICAD_FOOTPRINT_EXT, KICAD_3DMODEL_EXT
from . import file_manage as fm
from .Sexp_read_write import libtable_check_missing_entries
from .variables import lib_list_read, lib_list_write


class KicadSymFileHandler(FileSystemEventHandler):
    """
    Event handler class that triggers actions when `.kicad_sym` files are created or modified.

    Parameters
    ----------
    None

    Attributes
    ----------
    None
    """

    def on_created(self, event):
        """
        Called when a file or directory is created.

        Parameters
        ----------
        event : watchdog.events.FileSystemEvent
            The event object representing the file system event.

        Returns
        -------
        None
        """
        self._handle_event(event)

    # def on_modified(self, event):
    #     """
    #     Called when a file or directory is modified.

    #     Parameters
    #     ----------
    #     event : watchdog.events.FileSystemEvent
    #         The event object representing the file system event.

    #     Returns
    #     -------
    #     None
    #     """
    #     self._handle_event(event)

    def _handle_event(self, event):
        """
        Helper method to handle file creation and modification events.

        Parameters
        ----------
        event : watchdog.events.FileSystemEvent
            The event object representing the file system event.

        Returns
        -------
        None
        """
        # Check if the event is for a directory
        if event.is_directory:
            return
        file_path = Path(event.src_path)
        file = os.path.basename(file_path)

        if not os.path.exists(file_path):
            print(f"File {file} was already processed, skipping")
            return

        # Check if the file has the `.kicad_sym` extension
        if file.endswith(KICAD_SYMBOL_EXT) or file.endswith(KICAD_FOOTPRINT_EXT) or file.endswith(KICAD_3DMODEL_EXT):
            print(f"{file} will be added")
            all_libs = fm.libfolder_check_and_init()
            lib_list_write(all_libs)
            libtable_check_missing_entries(lib_list_read())
            fm.add_to_lib(file_path, file)
            print(f"{file} added")

def monitor_directory(path):
    """
    Monitor the specified directory for `.kicad_sym` files and delete them as they are created or renamed.
    Also performs an initial scan of the directory.

    Parameters
    ----------
    path : str
        The path to the directory to be monitored.

    Returns
    -------
    None
    """

    # Set up the event handler and observer
    event_handler = KicadSymFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
