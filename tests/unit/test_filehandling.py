from pathlib import Path
from cfsiv_utils import filehandling as fh



def test_clean_filename_str():
    data = ['qwerty~!@#$%^&*().ext', Path('qwerty~!@#$%^&().ext')]
    reslt = fh.clean_filename_str(data[0])
    assert data[1] == reslt



def test_new_name_if_exists():
    testname = fh.new_name_if_exists(Path('README.md'))
    assert testname == Path('README(1).md')
