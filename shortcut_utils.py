import os
import sys


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
    shortcut.TargetPath = exe_path
    shortcut.Arguments = "--play"
    shortcut.IconLocation = exe_path
    shortcut.WorkingDirectory = os.path.dirname(exe_path)
    shortcut.Description = "Grand Theft Auto: San Andreas"
    shortcut.save()

    return True
