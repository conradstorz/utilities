#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Standardize methods for file handling. 
    The functions include verifing filenames are safe for OS in use.
    Files are handled using the pathlib approach.
    Sub-Directory structures can be generated from timestamps.
    Sub-Directory structures can be generated from filenames.
"""

import csv
from os import error
from os import chdir as Change_Directory
from loguru import logger
from pathlib import Path
import shutil as _shutil
from shutil import SpecialFileError
from cfsiv_utils.time_strings import timefstring



@logger.catch
def write_csv(data, filename="temp.csv", directory="CSV_DATA", use_subs=False):
    """'data' is expected to be a list of dicts 
    Take data and write all fields to storage as csv with headers from keys.
    if filename already exists automatically append to end of file if headers match.

    with open(r'names.csv', 'a', newline='') as csvfile:
        fieldnames = ['This','aNew']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'This':'is', 'aNew':'Row'})

    Process: file exist? headers match? append data.
    file exist? headers mis-match. raise exception
    no file? create file and save data.
    """
    # create csv file path
    dirobj = Path(Path.cwd(), directory)
    dirobj.mkdir(parents=True, exist_ok=True)    
    pathobj = check_and_validate_fname(filename, dirobj)

    if not pathobj.exists():
        with open(pathobj, "w", newline="") as csvfile:
            csv_obj = csv.writer(csvfile, delimiter=",")
            headers = data[0].keys()
            csv_obj.writerow(headers)
    with open(pathobj, "a+", newline="") as csvfile:
        csv_obj = csv.writer(csvfile, delimiter=",")
        for item in data:  # data should be the list of dicts contaning observations/forecasts.
            csv_obj.writerow(item.values())
    return



def get_files(source_directory: Path, pattern=None):
    """Returns a list of all files from directory matching optional pattern.

    Args:
        source_directory (Path): Relative or absolute reference to a directory.
        pattern (str, optional): Filename matching pattern wildcards accepted. Defaults to '*.*'.

    Raises:
        TypeError: If optional inputs are out of bounds.

    Returns:
        list: A list of all files matching pattern from directory.
    """
    if pattern == None:
        pattern = '*.*'
    else:
        if type(pattern) != str:
            raise TypeError(f'pattern must be type string, got {type(pattern)}')
    if type(source_directory) != Path:
        logger.debug(f'source_directory must be type Path. Got: {type(source_directory)}')
        source_directory = Path(source_directory)        
    ORIGINAL_WORKING_DIRECTORY = Path.cwd()
    SOURCE_DIRECTORY = source_directory.resolve()
    if not(SOURCE_DIRECTORY.is_dir()):
        logger.error(f'Source_directory must be a valid dir. Got {source_directory}')
    NEW_WORKING_DIRECTORY = Path.cwd()    
    if SOURCE_DIRECTORY != ORIGINAL_WORKING_DIRECTORY:
        try:
            Change_Directory(SOURCE_DIRECTORY)
            NEW_WORKING_DIRECTORY = Path.cwd()
        except error as e:
            logger.error(f'Could not access source directory: {e}')
    if SOURCE_DIRECTORY != NEW_WORKING_DIRECTORY:
        logger.error('Unknown change directory to source error.')
        raise FileNotFoundError(f'Could not access source_Path: {source_directory}')
    try:
        files = list(SOURCE_DIRECTORY.rglob(pattern))
    except error as e:
        logger.error(f'Error locating files matching pattern: {pattern}')
        files = []
    # TODO return cwd to original location.
    try:
        Change_Directory(ORIGINAL_WORKING_DIRECTORY)
    except error as e:
        logger.error(f'Could not restore original directory: {e}')    
    return files



def clean_filename_str(fn: str):
    """Replace invalid characters from provided string.
        Note: '-' is invalid in windows if it is the last character in a name following a space character.
        # TODO replace invalid characters with underscores.
    """
    return Path("".join(i for i in fn if i not in "\/:*?<>|-"))



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



def create_timestamp_subdirectory_Structure(file: Path, target_directory=None):
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
    return new_path



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
    new_path = create_timestamp_subdirectory_Structure(file, target_directory=target_directory)
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



def check_and_validate_fname(fname, target_directory=None):
    """Remove invalid characters in filename, combine with target_directory (optional)
    and optionaly create a new filename that doesn't already exist at destination.  

    Args:
        fname (Path): filename to fix.
        target_directory (Path, optional): defaults to current working directory.
        rename (bool, optional): generates a name that is unique. Defaults to False.

    Returns:
        Path: Path object that is valid.
    """
    if target_directory == None:
        target_directory = Path.cwd() # defaults to the current working directory.
    else:
        if type(target_directory) != Path:
            logger.debug(f'target directory must be a valid Path, got {type(target_directory)}')
    clean_name = clean_filename_str(fname)
    target_directory.mkdir(parents=True, exist_ok=True)
    return Path(target_directory, clean_name)



@logger.catch
def Main():
    try:
        filelist = get_files(Path('Q:'), pattern='*takeout*.zip')
    except FileNotFoundError as e:
        filelist = []
        print(f'Bad Path: {e}')
    print(len(filelist))


    data = ['qwerty~!@#$%^&*().ext', Path('qwerty~!@#$%^&().ext')]
    reslt = clean_filename_str(data[0])
    assert data[1] == reslt

    testname = new_name_if_exists(Path('README.md'))
    assert testname == Path('README(1).md')

    # copy_to_target(

    # copy_to_target_and_divide_by_filedate(

    # copy_to_target_and_divide_by_dictionary(

    # check_and_validate_fname(


if __name__ == '__main__':
    Main()

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

