"""
Misc methods for the plugin handling.

@date: Feb 20, 2013
@author: CarolinaFernandez
"""

import os

def join_paths(path_list=[]):
    path = ""
    for pl in path_list:
        if isinstance(pl, list):
            pl = pl[0]
        path = os.path.join(path, pl)
    return path

class Singleton(type):

    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

