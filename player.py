import os
import subprocess
import sys
import tempfile
import time
import tkinter as tk

import cv2
import pygame
from PIL import Image, ImageTk
from imageio_ffmpeg import get_ffmpeg_exe

from resources import ICON_PATH, VIDEO_PATH

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
    playback_start = None

    def show_frame():
        nonlocal first_frame, playback_start
        if roasted:
            return

        if playback_start is None:
            playback_start = time.monotonic()

        # figure out which frame we *should* be on right now based on the
        # real clock, and skip/drop frames to catch up if rendering has
        # fallen behind (e.g. CPU contention from the screen recorder) --
        # without this, a slow frame just pushes every frame after it
        # later and the whole video visibly plays in slow motion while
        # the audio (which pygame paces independently) stays on time
        target_frame_index = int((time.monotonic() - playback_start) * fps)
        current_frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        frames_to_skip = target_frame_index - current_frame_index
        if frames_to_skip > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_index + frames_to_skip)

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

        # schedule the next check soon rather than a full frame-delay away,
        # so we notice quickly if we need to catch up again
        root.after(max(1, delay // 3), show_frame)

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
            # during the intro, Escape does nothing -- only Enter skips ahead
        elif event.keysym == "Return":
            skip_to_roast()
        return "break"

    root.bind("<Key>", on_key)

    show_frame()
    root.mainloop()
