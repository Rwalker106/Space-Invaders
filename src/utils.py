import sys
import os


def resource_path(relative_path):
    """Resolve path to a bundled asset. Works in both dev and PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)


def user_data_path(filename):
    """Resolve path for writable user data (high scores, saves).
    In a PyInstaller bundle writes next to the .exe, not inside it."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(os.path.dirname(sys.executable), filename)
    return os.path.join(os.path.abspath('.'), filename)
