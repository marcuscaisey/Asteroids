import os
import sys


def find_asset(asset):
    """
    Find asset depending on whether game is frozen or not.

    If game is frozen then all assets will be in build directory rather
    than the assets directory.
    """
    if getattr(sys, 'frozen', False):
        # Need to strip base directories from asset path
        asset = os.path.basename(asset)
        asset_dir = os.path.dirname(sys.executable)
    else:
        current_dir = os.path.abspath(os.path.dirname(__file__))
        asset_dir = os.path.join(current_dir, '..\\assets\\')
    return os.path.join(asset_dir, asset)
