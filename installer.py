import sys


def main():
    if "--play" in sys.argv:
        from player import run_player
        run_player()
    else:
        from wizard import run_wizard
        run_wizard()


if __name__ == "__main__":
    main()
