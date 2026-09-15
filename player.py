import tkinter as tk

import cv2
from PIL import Image, ImageTk

from resources import VIDEO_PATH

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


def draw_mute_icon(canvas):
    # just a speaker shape with a line through it, purely for looks,
    # nothing is bound to clicks on it
    canvas.create_polygon(6, 18, 16, 18, 27, 8, 27, 34, 16, 24, 6, 24,
                           fill="white", outline="white")
    canvas.create_line(4, 4, 36, 36, fill="#e53935", width=4)
    canvas.create_line(4, 36, 36, 4, fill="#e53935", width=4)


def run_player():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg="black", cursor="none")

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    video_label = tk.Label(root, bg="black", bd=0, highlightthickness=0)
    video_label.place(x=0, y=0, width=screen_w, height=screen_h)

    mute_canvas = tk.Canvas(root, width=40, height=40, bg="black", highlightthickness=0)
    mute_canvas.place(x=24, y=24)
    draw_mute_icon(mute_canvas)

    cap = cv2.VideoCapture(VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 1:
        fps = 30
    delay = int(1000 / fps)

    def show_roast():
        video_label.place_forget()
        mute_canvas.place_forget()

        roast_label = tk.Label(
            root,
            text=ROAST_LINES,
            fg="#f7941d",
            bg="black",
            font=("Consolas", 15, "bold"),
            justify="center",
        )
        roast_label.place(relx=0.5, rely=0.5, anchor="center")

    def show_frame():
        ok, frame = cap.read()
        if not ok:
            cap.release()
            show_roast()
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame).resize((screen_w, screen_h))
        photo = ImageTk.PhotoImage(image=img)

        video_label.photo = photo  # keep a ref or tkinter will drop the frame
        video_label.configure(image=photo)

        root.after(delay, show_frame)

    def on_key(event):
        if event.keysym == "Escape":
            root.destroy()
        return "break"

    root.bind("<Key>", on_key)

    show_frame()
    root.mainloop()
