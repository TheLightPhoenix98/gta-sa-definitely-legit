import sys


def enable_dpi_awareness():
    # without this, Windows scales the whole window like a bitmap on
    # anything above 100% display scaling (125%/150% is extremely common
    # on laptops), which is exactly what makes a fixed-size Tkinter window
    # look blurry and clip content outside its own borders
    if sys.platform != "win32":
        return
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            import ctypes
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def main():
    enable_dpi_awareness()

    if "--play" in sys.argv:
        from player import run_player
        run_player()
    else:
        from wizard import run_wizard
        run_wizard()


if __name__ == "__main__":
    main()
