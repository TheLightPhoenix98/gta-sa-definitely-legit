import os
import random
import shutil
import subprocess
import sys
import tempfile
import time
import tkinter as tk

import cv2
import pygame
from PIL import Image, ImageTk
from imageio_ffmpeg import get_ffmpeg_exe

from resources import VIDEO_PATH, ICON_PATH

ROAST_LINES = (
    "CONGRATULATIONS, MAHI! YOU JUST INSTALLED ABSOLUTELY NOTHING.\n\n"
    "Free Game Finding Skill: 0/10\n"
    "Patience Wasted: 100%\n"
    "IQ Level: Lower than CJ's respect bar at the start of the game.\n\n"
    "You really thought Rockstar Games sent a custom 2004 nostalgia\n"
    "installer just for you? Bro, even Big Smoke wouldn't trust a\n"
    "download link this sketchy.\n\n"
    "Instead of chasing free GTAs, go follow the damn train or buy\n"
    "some original games. Now close this installer, get off your\n"
    "potato PC, and go touch some real-life San Andreas grass! \U0001F335\U0001F697\U0001F4A5\n\n"
    "btw, I'm Xtrimlee sorrie. Ekhon exit korte keyboard er ESC press kor"
)

NOTEPAD_PRANK_DELAY_SECONDS = 4
NOTEPAD_PRANK_TEXT = "Prank Like A Dev"


def _human_type(shell, text):
    # sends one keystroke at a time with a randomized delay so it reads
    # like someone actually typing, instead of the whole string appearing
    # in one instant paste
    for ch in text:
        shell.SendKeys(ch)
        time.sleep(random.uniform(0.09, 0.24))
        # small chance of a slightly longer pause, like a person
        # thinking mid-word
        if random.random() < 0.12:
            time.sleep(random.uniform(0.15, 0.35))


def run_notepad_prank():
    # best-effort only: skip silently on anything that isn't set up for
    # it (no pywin32, no notepad on PATH, etc) -- this is a bonus prank
    # on top of the roast, not something the rest of the program should
    # ever depend on or crash over
    try:
        import win32com.client
    except ImportError:
        print("pywin32 not available, skipping notepad prank")
        return

    notepad_path = shutil.which("notepad") or shutil.which("notepad.exe")
    if not notepad_path:
        print("notepad not found on PATH, skipping notepad prank")
        return

    try:
        subprocess.Popen([notepad_path])
    except Exception as e:
        print("Couldn't launch notepad:", e)
        return

    shell = win32com.client.Dispatch("WScript.Shell")

    # give notepad a moment to actually open and register its window
    # before trying to bring it to the foreground
    time.sleep(1)
    try:
        shell.AppActivate("Notepad")
    except Exception:
        pass
    time.sleep(0.3)

    try:
        _human_type(shell, NOTEPAD_PRANK_TEXT)
    except Exception as e:
        print("Notepad typing failed:", e)


def extract_audio(video_path):
    # pulls the audio track out to a temp wav using the ffmpeg binary
    # that imageio-ffmpeg ships with, so we don't need a system install
    # of ffmpeg on whatever PC this ends up running on
    ffmpeg_exe = get_ffmpeg_exe()
    tmp_wav = os.path.join(tempfile.gettempdir(), "gta_sa_intro_audio.wav")

    cmd = [
        ffmpeg_exe, "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2",
        tmp_wav,
    ]

    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    creationflags=creationflags)
    return tmp_wav


def run_player():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg="black", cursor="none")
    try:
        root.iconbitmap(ICON_PATH)
    except Exception:
        pass

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    video_label = tk.Label(root, bg="black", bd=0, highlightthickness=0)
    video_label.place(x=0, y=0, width=screen_w, height=screen_h)

    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 30
    delay = int(1000 / fps)

    # best-effort audio - if anything about this fails (no audio device,
    # extraction hiccup, whatever) just fall back to playing silently
    # instead of crashing the whole thing
    wav_path = None
    try:
        pygame.mixer.init()
        wav_path = extract_audio(VIDEO_PATH)
        pygame.mixer.music.load(wav_path)
    except Exception as e:
        print("Audio setup failed, playing without sound:", e)
        wav_path = None

    def stop_audio():
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    roasted = False

    def show_roast():
        nonlocal roasted
        if roasted:
            return
        roasted = True

        video_label.place_forget()
        stop_audio()

        roast_label = tk.Label(
            root,
            text=ROAST_LINES,
            fg="#f7941d",
            bg="black",
            font=("Consolas", 15, "bold"),
            justify="center",
        )
        roast_label.place(relx=0.5, rely=0.5, anchor="center")

    first_frame = True

    def show_frame():
        nonlocal first_frame
        if roasted:
            return

        ok, frame = cap.read()
        if not ok:
            cap.release()
            show_roast()
            return

        if first_frame:
            first_frame = False
            if wav_path:
                try:
                    pygame.mixer.music.play()
                except Exception as e:
                    print("Couldn't start audio playback:", e)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame).resize((screen_w, screen_h))
        photo = ImageTk.PhotoImage(image=img)

        video_label.photo = photo  # keep a ref or tkinter will drop the frame
        video_label.configure(image=photo)

        root.after(delay, show_frame)

    def skip_to_roast():
        if roasted:
            return
        cap.release()
        show_roast()

    def on_key(event):
        if event.keysym == "Escape":
            if roasted:
                stop_audio()
                root.destroy()
                # window is already closed at this point, so a blocking
                # wait here is fine -- nothing else is left on screen
                time.sleep(NOTEPAD_PRANK_DELAY_SECONDS)
                run_notepad_prank()
            # during the intro, Escape does nothing -- only Enter skips ahead
        elif event.keysym == "Return":
            skip_to_roast()
        return "break"

    root.bind("<Key>", on_key)

    show_frame()
    root.mainloop()
