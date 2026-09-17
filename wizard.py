import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random

from PIL import Image, ImageTk

from resources import ICON_PATH, MAIN_LOGO_PATH, BANNER_PATH, SIDEBAR_PATH, ROCKSTAR_LOGO_PATH
from shortcut_utils import create_desktop_shortcut

WINDOW_W = 780
WINDOW_H = 500

ACCENT = "#f7941d"
BG_DARK = "#141414"
BG_PANEL = "#1c1c1c"
TEXT_LIGHT = "#eaeaea"
TEXT_DIM = "#a0a0a0"

LICENSE_TEXT = """ROCKSTAR GAMES END USER LICENSE AGREEMENT
Grand Theft Auto: San Andreas - Definitive Edition (Definitely Not Pirated)

PLEASE READ THIS AGREEMENT CAREFULLY. BY CLICKING "I AGREE," YOU CONFIRM
THAT YOU HAVE READ NOTHING BELOW AND JUST WANT TO PLAY THE GAME.

1. GRANT OF LICENSE
Rockstar Games hereby grants you a limited, non-transferable, "we both
know you didn't pay for this" license to install one (1) copy of San
Andreas on one (1) potentially very old laptop.

2. SYSTEM REQUIREMENTS
Your PC must have at least 512MB of hope and a CD drive that hasn't
been used since 2009.

3. USER CONDUCT
You agree not to blame the developers when CJ's bike glitches through
a mountain. This is a known feature, not a bug.

4. NO REFUNDS
There are no refunds, because there was no payment. You know what
you did.

5. DATA COLLECTION
We collect nothing except your dignity, which you forfeited the
moment you clicked "Install" on a game from 2004.

6. ACKNOWLEDGEMENT
By clicking "I Agree" you acknowledge that you skipped reading this
entire document, just like every license agreement in human history.
"""

FAKE_FILES = [
    "gta_sa.exe", "gta_sa.dat", "models\\cj_ped.dff", "textures\\vinewood.txd",
    "audio\\radio_bounce_fm.wav", "audio\\radio_kdst.wav", "script\\main.scm",
    "data\\handling.cfg", "data\\weapon.dat", "maps\\los_santos.ipl",
    "maps\\san_fierro.ipl", "maps\\las_venturas.ipl", "textures\\hud.txd",
    "movies\\intro.mp4", "save\\GTASAsf1.b", "config\\graphics.cfg",
    "redist\\directx_runtime.exe", "redist\\vcredist_x86.exe",
]


def load_image(path, size):
    img = Image.open(path).convert("RGBA")
    img = img.resize(size, Image.LANCZOS)
    return ImageTk.PhotoImage(img)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grand Theft Auto: San Andreas - Setup Wizard")
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)
        self.configure(bg=BG_DARK)

        try:
            self.iconbitmap(ICON_PATH)
        except Exception:
            pass

        # keep references around so PhotoImage objects don't get garbage collected
        self.images = {
            "sidebar": load_image(SIDEBAR_PATH, (170, WINDOW_H)),
            "banner": load_image(BANNER_PATH, (560, 140)),
            "rockstar": load_image(ROCKSTAR_LOGO_PATH, (46, 42)),
            "logo_small": load_image(MAIN_LOGO_PATH, (90, 90)),
            "logo_big": load_image(MAIN_LOGO_PATH, (140, 140)),
        }

        container = tk.Frame(self, bg=BG_DARK)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for PageClass in (WelcomePage, LicensePage, LocationPage, ComponentsPage, ProgressPage, FinishPage):
            page = PageClass(container, self)
            self.frames[PageClass.__name__] = page
            page.place(x=0, y=0, width=WINDOW_W, height=WINDOW_H)

        self.show_frame("WelcomePage")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()


class BasePage(tk.Frame):
    """Common chrome shared by every wizard page: sidebar on the left,
    rockstar logo top right, nav buttons at the bottom."""

    def __init__(self, parent, controller, title):
        super().__init__(parent, bg=BG_DARK)
        self.controller = controller

        sidebar = tk.Label(self, image=controller.images["sidebar"], bd=0)
        sidebar.place(x=0, y=0)

        rockstar_logo = tk.Label(self, image=controller.images["rockstar"], bg=BG_DARK, bd=0)
        rockstar_logo.place(x=WINDOW_W - 66, y=14)

        title_label = tk.Label(self, text=title, bg=BG_DARK, fg=ACCENT,
                                font=("Segoe UI", 16, "bold"))
        title_label.place(x=190, y=16)

        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.place(x=190, y=60, width=WINDOW_W - 210, height=350)

        self.nav = tk.Frame(self, bg=BG_PANEL, height=48)
        self.nav.place(x=170, y=WINDOW_H - 48, width=WINDOW_W - 170, height=48)

        # positions are relative to the nav frame, whose width is
        # (WINDOW_W - 170) -- not WINDOW_W. All three buttons + their
        # margins/gaps must fit inside that width or they clip off the
        # window's right edge.
        NAV_W = WINDOW_W - 170

        self.cancel_btn = tk.Button(self.nav, text="Cancel", width=10, command=controller.destroy)
        self.cancel_btn.place(x=NAV_W - 100, y=8)

        self.next_btn = tk.Button(self.nav, text="Next >", width=10, command=self.go_next)
        self.next_btn.place(x=NAV_W - 214, y=8)

        self.back_btn = tk.Button(self.nav, text="< Back", width=10, command=self.go_back)
        self.back_btn.place(x=NAV_W - 304, y=8)

    def go_back(self):
        pass

    def go_next(self):
        pass


class WelcomePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Welcome")
        self.back_btn.config(state="disabled")
        self.next_btn.config(text="Next >", command=self.go_next)

        banner = tk.Label(self.content, image=controller.images["banner"], bg=BG_DARK, bd=0)
        banner.pack(pady=(0, 16))

        text = tk.Label(
            self.content,
            text="Welcome to the Grand Theft Auto: San Andreas Setup Wizard.\n"
                 "This wizard will guide you through the installation.\n\n"
                 "It is strongly recommended that you close all other\n"
                 "applications before continuing.",
            bg=BG_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 10), justify="left",
        )
        text.pack(anchor="w")

    def go_next(self):
        self.controller.show_frame("LicensePage")


class LicensePage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "License Agreement")

        text_frame = tk.Frame(self.content, bg=BG_DARK)
        text_frame.pack(pady=(0, 8))

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        box = tk.Text(text_frame, wrap="word", height=14, width=60,
                       bg="#0f0f0f", fg=TEXT_LIGHT, relief="flat",
                       font=("Consolas", 9), yscrollcommand=scrollbar.set)
        box.insert("1.0", LICENSE_TEXT)
        box.config(state="disabled")
        box.pack(side="left")

        scrollbar.config(command=box.yview)

        self.agree_var = tk.BooleanVar(value=False)
        check = tk.Checkbutton(
            self.content, text="I have read and agree to the terms",
            variable=self.agree_var, command=self.toggle_next,
            bg=BG_DARK, fg=TEXT_LIGHT, selectcolor=BG_PANEL,
            activebackground=BG_DARK, activeforeground=TEXT_LIGHT,
        )
        check.pack(anchor="w")

        self.next_btn.config(state="disabled")

    def toggle_next(self):
        self.next_btn.config(state="normal" if self.agree_var.get() else "disabled")

    def go_back(self):
        self.controller.show_frame("WelcomePage")

    def go_next(self):
        if self.agree_var.get():
            self.controller.show_frame("LocationPage")


class LocationPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Choose Install Location")

        label = tk.Label(
            self.content,
            text="Setup will install Grand Theft Auto: San Andreas in the\n"
                 "following folder. To install in a different folder, click\n"
                 "Browse and select another folder.",
            bg=BG_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 10), justify="left",
        )
        label.pack(anchor="w", pady=(0, 20))

        path_row = tk.Frame(self.content, bg=BG_DARK)
        path_row.pack(fill="x")

        self.path_var = tk.StringVar(value=r"C:\Program Files (x86)\Rockstar Games\GTA San Andreas")
        entry = tk.Entry(path_row, textvariable=self.path_var, width=45,
                          bg="#0f0f0f", fg=TEXT_LIGHT, insertbackground=TEXT_LIGHT, relief="flat")
        entry.pack(side="left", ipady=4, padx=(0, 8))

        browse_btn = tk.Button(path_row, text="Browse...", command=self.browse)
        browse_btn.pack(side="left")

        space_label = tk.Label(
            self.content, text="\nSpace required: 4.7 GB\nSpace available: (does it really matter?)",
            bg=BG_DARK, fg=TEXT_DIM, font=("Segoe UI", 9), justify="left",
        )
        space_label.pack(anchor="w", pady=(20, 0))

    def browse(self):
        chosen = filedialog.askdirectory()
        if chosen:
            self.path_var.set(chosen)

    def go_back(self):
        self.controller.show_frame("LicensePage")

    def go_next(self):
        self.controller.show_frame("ComponentsPage")


class ComponentsPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Select Components")

        label = tk.Label(
            self.content, text="Select the components you want to install:",
            bg=BG_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 10),
        )
        label.pack(anchor="w", pady=(0, 12))

        components = [
            "Main Game Files (required)",
            "HD Textures Pack",
            "Bonus Radio Soundtrack",
            "DirectX 9 Runtime",
            "Desktop Shortcut",
        ]
        for i, comp in enumerate(components):
            var = tk.BooleanVar(value=True)
            state = "disabled" if i == 0 else "normal"
            cb = tk.Checkbutton(
                self.content, text=comp, variable=var, state=state,
                bg=BG_DARK, fg=TEXT_LIGHT, selectcolor=BG_PANEL,
                activebackground=BG_DARK, activeforeground=TEXT_LIGHT,
            )
            cb.pack(anchor="w", pady=2)

    def go_back(self):
        self.controller.show_frame("LocationPage")

    def go_next(self):
        self.controller.show_frame("ProgressPage")


class ProgressPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Installing")
        self.back_btn.config(state="disabled")
        self.next_btn.config(state="disabled")
        self.started = False

        label = tk.Label(
            self.content, text="Please wait while Setup installs Grand Theft Auto: San Andreas.",
            bg=BG_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 10),
        )
        label.pack(anchor="w", pady=(0, 16))

        self.progress = ttk.Progressbar(self.content, length=460, mode="determinate", maximum=100)
        self.progress.pack(anchor="w", pady=(0, 12))

        self.file_label = tk.Label(
            self.content, text="", bg=BG_DARK, fg=TEXT_DIM, font=("Consolas", 9),
        )
        self.file_label.pack(anchor="w")

    def on_show(self):
        if self.started:
            return
        self.started = True
        self.pct = 0
        self.run_step()

    def run_step(self):
        if self.pct >= 100:
            self.file_label.config(text="Installation complete.")
            def _go_finish():
                if not self.controller.winfo_exists():
                    return
                self.controller.show_frame("FinishPage")
            self.controller.after(700, _go_finish)
            return

        step = random.randint(1, 3)
        self.pct = min(100, self.pct + step)
        self.progress["value"] = self.pct

        fake_file = random.choice(FAKE_FILES)
        self.file_label.config(text=f"Copying: {fake_file}")

        # random delay so it doesn't look suspiciously linear -- tuned so
        # the whole bar takes ~15-17s total, which reads as plausible for
        # a "4.7GB install" instead of finishing in a blink
        delay = random.randint(200, 450)
        self.controller.after(delay, self.run_step)


class FinishPage(BasePage):
    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Setup Complete")
        self.back_btn.config(state="disabled")
        self.next_btn.config(text="Finish", command=self.finish)

        logo = tk.Label(self.content, image=controller.images["logo_big"], bg=BG_DARK, bd=0)
        logo.pack(pady=(0, 12))

        text = tk.Label(
            self.content,
            text="Setup has finished installing Grand Theft Auto: San Andreas\n"
                 "on your computer.\n\n"
                 "A shortcut has been placed on your desktop.",
            bg=BG_DARK, fg=TEXT_LIGHT, font=("Segoe UI", 10), justify="left",
        )
        text.pack(anchor="w")

    def finish(self):
        create_desktop_shortcut()
        self.controller.destroy()


def run_wizard():
    app = App()
    app.mainloop()
