# License

"""
Module-level entry level point for the add-on
"""
from ._version import __version__


def init_addon():
    # error check
    from . import main


init_addon()