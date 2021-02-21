#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Standardize methods for file handling. 
    The functions include verifing filenames are safe for OS in use.
    Files are handled using the pathlib approach.
    Data can be saved in flat CSV files from several types of data formats.
    Sub-Directory structures can be generated from timestamps.
    CSV files get appended if they already exist.
"""

from os import error
from pathlib import Path
import shutil as _shutil
from shutil import SpecialFileError
from time_strings import timefstring


def clean_filename_str(fn):
    """Replace invalid characters from provided string with underscores.
        Note: '-' is invalid in windows if it is the last character in a name.
    """
    return Path("_".join(i for i in fn if i not in "\/:*?<>|-"))



def new_name_if_exists(file: Path):
    """Make a new filename that avoids name collisions.
        example: filename(xx).ext where xx is incremented until 
        unused filename is created.

        Args:
            file (Path): proposed unique filename.

        Returns:
            Path_obj: Guaranteed unique filename.
    """
    new_name = file
    i = 1
    while True:
        if not new_name.is_file():
            return new_name
        else:
            new_name = file.with_name(f"{file.stem}({i}){file.suffix}")
            i += 1



def copy_to_target(file: Path, target_diectory=None):
    """Copy offered file to new location
        while ensuring not to overwrite any existing file.

    Args:
        file (Path): Filename to copy to new location.
        target_directory (Path, optional): must be a valid Path if provided.
            Current working directory will be used as default if not provided.

    Returns:
        bool: Always returns True unless 'SpecialFileError' is raised.
    """
    if target_diectory == None:
        target_diectory = Path.cwd()
    else:
        if type(target_diectory) != Path:
            raise FileNotFoundError(f'target_directory must be type Path, got {type(target_diectory)}')
    new_file = new_name_if_exists(target_diectory / file.name)
    try:
        _shutil.copy2(file, new_file)
    except error as e:
        raise SpecialFileError(f"could not copy file '{file}' due to: {e}")
    return True



def copy_to_target_and_divide_by_filedate(file: Path, target_directory=None):
    """Generate a destination for the offered file based on its' timestamp.
        Destination is in the form root/year/month/filename.ext

    Args:
        file (Path): File to copy as a Path_obj
        target_directory (Path, optional): defaults to current working directory.

    Returns:
        bool: Always returns True at this point.
    """
    if target_directory == None:
        target_directory = Path.cwd()
    else:
        if type(target_directory) != Path:
            raise TypeError(f'target directory must be a valid Path, got {type(target_directory)}')
    creation_date = file.stat().st_mtime # in windows this is closer to the oldest date on the file.
    # st_ctime will be equal to the most recent time the file was copied from place to place.
    date = timefstring(creation_date)
    new_path = target_directory / f"{date.year}/{date.month:02}/"
    new_path.mkdir(parents=True, exist_ok=True)
    return copy_to_target(file.name, new_path)



def copy_to_target_and_divide_by_dictionary(file: Path, target_directory=None, characters=None):
    """Generate a destination for the offered file based on its' name.
        Destination is in the form root/(first 'x' characters of filename)/filename.ext

    Args:
        file (Path): File to copy as a Path_obj
        target_directory (Path, optional): root directory for destination.
        characters (integer, optional): number of characters from filename to use.

    Returns:
        bool: status of copy process.
    """
    if characters == None:
        characters = 1 # defaults to the first character of the filename.
    else:
        if type(characters) != int:
            raise(f'characters value must be integer, got {type(characters)}')
    if target_directory == None:
        target_directory = Path.cwd() # defaults to the current working directory.
    else:
        if type(target_directory) != Path:
            raise TypeError(f'target directory must be a valid Path, got {type(target_directory)}')
    new_path = target_directory / f"{file.name[0:characters]}/"
    new_path.mkdir(parents=True, exist_ok=True)
    return copy_to_target(file.name, new_path)



def check_and_validate(fname, target_directory=None, rename=None):
    """Replace invalid characters in filename with underscore, combine with target_directory (optional)
    and optionaly create a new filename that doesn't already exist at destination.  

    Args:
        fname (Path): filename to fix.
        target_directory (Path, optional): defaults to current working directory.
        rename (bool, optional): generates a name that is unique. Defaults to False.

    Returns:
        Path: Path object that is valid and does not exist.
    """
    if target_directory == None:
        target_directory = Path.cwd() # defaults to the current working directory.
    else:
        if type(target_directory) != Path:
            raise TypeError(f'target directory must be a valid Path, got {type(target_directory)}')
    if rename == None:
        rename = False # default
    else:
        if type(rename) != bool:
            raise TypeError(f'rename must be Bool, got {type(rename)}')            
    clean_name = clean_filename_str(fname)
    target_directory.mkdir(parents=True, exist_ok=True)
    OUT_PATH_HANDLE = Path(target_directory, clean_name)
    if OUT_PATH_HANDLE.is_file():
        if rename:
            unique_name = new_name_if_exists(OUT_PATH_HANDLE)
        else:
            return None
    return unique_name



# NOTES FOR USE OF pathlib

""" access parts of a filename:
>>> Path('static/dist/js/app.min.js').name
'app.min.js'
>>> pathobj = Path('static/dist/js/app.min.js')
>>> print(pathobj.name)
'app.min.js'
>>> Path('static/dist/js/app.min.js').suffix
'.js'
>>> Path('static/dist/js/app.min.js').suffixes
'.min.js'
>>> Path('static/dist/js/app.min.js').stem
'app'
"""

# set your reference point with the location of the python file you’re writing in
# this_file = Path(__file__)

# Here are three ways to get the folder of the current python file
# this_folder1 = Path(__file__, "..")
# this_folder2 = Path(__file__) / ".."
# this_folder3 = Path(__file__).parent

# This will fail:
# assert this_folder1 == this_folder2 == this_folder3
# becasue the variables are relative paths.

# The resolve() method removes '..' segments, follows symlinks, and returns
# the absolute path to the item.
# this works:
# assert this_folder1.resolve() == this_folder2.resolve() == this_folder3.resolve()


# folder_where_python_was_run = Path.cwd()

# create a new folder:
# Path("/my/directory").mkdir(parents=True, exist_ok=True)

# find path to your running code
# project_root = Path(__file__).resolve().parents[1] # this is the folder 2 levels up from your running code.

# create a new PathObj:
# static_files = project_root / 'static' # if you like this sort of thing they overrode the divide operator.
# media_files = Path(project_root, 'media') # I prefer this method.

# how to define 2 sub-directories at once:
# compiled_js_folder = static_files.joinpath('dist', 'js') # this is robust across all OS.

# gather items from specified path
# list(static_files.iterdir()) # returns a list of all items in directory.
# [x for x in static_files.iterdir if x.is_dir()] # list of only directories in a folder.
# [x for x in static_files.iterdir if x.is_file()] # same for files only.

# get a list of items matching a pattern:
# files = list(compiled_js_folder.glob('*.js')) # returns files ending with '.js'.

# sort the list of files by timestamp:
# files.sort(key=lambda fn: fn.stat().st_atime)
# atime, mtime, ctime don't seem to mean what I think. (Pathlib error?)

# search recursively down your folders path:
# sorted(project_root.rglob('*.js'))

# verify a path exists:
# Path('relative/path/to/nowhere').exists() # returns: False

# Example of directory deletion by pathlib
# pathobj = Path("demo/")
# pathobj.rmdir()

# Example of file deletion by pathlib
# pathobj = Path("demo/testfile.txt")
# pathobj.unlink()

