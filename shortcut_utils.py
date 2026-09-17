import os
import sys

from resources import ICON_PATH


def create_desktop_shortcut():
    # win32com is only available on Windows, this whole thing is a no-op
    # anywhere else (e.g. if someone runs the .py on Linux/Mac for testing)
    try:
        import win32com.client
    except ImportError:
        print("pywin32 not available, skipping shortcut creation")
        return False

    exe_path = sys.executable

    shell = win32com.client.Dispatch("WScript.Shell")
    desktop = shell.SpecialFolders("Desktop")
    shortcut_path = os.path.join(desktop, "GTA SA - Shortcut.lnk")

    shortcut = shell.CreateShortCut(shortcut_path)

    if getattr(sys, "frozen", False):
        # running as a PyInstaller-built exe: the exe itself is the target,
        # no script path needed
        shortcut.TargetPath = exe_path
        shortcut.Arguments = "--play"
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
    else:
        # running as a plain .py during dev: target has to be python.exe,
        # with the script path as the first argument, otherwise double
        # clicking the shortcut just opens a bare interpreter and does
        # nothing
        script_path = os.path.abspath(sys.argv[0])
        shortcut.TargetPath = exe_path
        shortcut.Arguments = f'"{script_path}" --play'
        shortcut.WorkingDirectory = os.path.dirname(script_path)

    shortcut.IconLocation = ICON_PATH
    shortcut.Description = "Grand Theft Auto: San Andreas"
    shortcut.save()

    return True
