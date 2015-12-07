import os
import sys

# Allow stercus module to be imported.
def insert_path():
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    root_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))
    sys.path.insert(0, root_dir)
