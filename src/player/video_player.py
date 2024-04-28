import tkinter as tk
from tkinter import filedialog
import vlc
from time import sleep


def setup_player():
    return vlc.MediaPlayer()


def create_initial_layout(root):
    # Clear the root window
    for widget in root.winfo_children():
        widget.destroy()

    # Make the 'root' the main window for file selection.
    entry_file = tk.Entry(root, width=50)
    entry_file.pack(side=tk.LEFT)

    def browse_file():
        filepath = filedialog.askopenfilename(filetypes=(("Video Files", "*.mp4"),))
        entry_file.delete(0, tk.END)
        entry_file.insert(0, filepath)

    def on_load():
        root.video_path = entry_file.get()
        root.quit()

    root.video_path = None
    tk.Label(root, text="Please select a video file:").pack()
    tk.Button(root, text="Browse", command=browse_file).pack(side=tk.LEFT)
    tk.Button(root, text="Load Video", command=on_load).pack()

    root.mainloop()
    return root.video_path
