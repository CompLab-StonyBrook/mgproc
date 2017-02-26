# __init__.py

import os
import re
from pprint import pprint

from io_tree import *
from tree_values import *
from metrics import *
from comparisons import *
from helpers import *


def load_user_code(user_file: str=None,
                   user_dir: str='./usercode'):
    """
    Load user-defined code.

    The user may want to define new tree traversals or new functions to be used
    by metrics. To simplify this, users can just add Python files to a user_dir
    folder.

    Parameters
    ----------
    user_file: str
        specific file to be loaded; by default, all files are loaded
    user_dir: str
        folder from which .py files are to be loaded; defaults to './usercode'
    """
    if user_file:
        user_files = [os.path.join(user_dir, user_file)]
    else:
        user_files = [os.path.join(user_dir, user_file)
                      for user_file in os.listdir(user_dir)
                      if user_file.endswith('py')]

    # execute code in each file and
    # add it to list of globally accessible functions
    for user_file in user_files:
        with open(user_file, 'r') as code_file:
            code = code_file.read()
            code_file.close()
            exec(code, globals())

load_user_code()
