import os
import sys


def resource_path(relative_path):
    # PyInstaller unpacks bundled files into a temp folder at runtime and
    # stores that path in sys._MEIPASS. Falls back to cwd when just running
    # the .py directly (dev mode).
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


ICON_PATH = resource_path(os.path.join("assets", "app_icon.ico"))
MAIN_LOGO_PATH = resource_path(os.path.join("assets", "main_logo.png"))
BANNER_PATH = resource_path(os.path.join("assets", "banner.jpg"))
SIDEBAR_PATH = resource_path(os.path.join("assets", "sidebar.jpeg"))
ROCKSTAR_LOGO_PATH = resource_path(os.path.join("assets", "rockstar_logo.png"))
VIDEO_PATH = resource_path(os.path.join("assets", "intro.mp4"))
