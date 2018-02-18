import os


def abs_asset_path(asset_path):
    """
    Return absolute path to asset where asset_path is given relative to
    assets.
    """
    current_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(current_dir, '../assets/' + asset_path)
