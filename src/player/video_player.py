import tkinter as tk
from tkinter import filedialog
import vlc
from time import sleep


def setup_player():
    return vlc.MediaPlayer()


def file_selection_layout(root):
    # Label to instruct the user
    label = tk.Label(root, text="Please select a video file:", font=("Helvetica", 14))
    label.pack(padx=10, pady=5)  # Add padding around the label

    # Entry widget to display the file path
    entry_file = tk.Entry(root, width=50)
    entry_file.pack(side=tk.LEFT, padx=10, pady=5)  # Add padding around the entry

    # Function to open a file dialog and update the entry with the selected file path
    def browse_file():
        filepath = filedialog.askopenfilename(filetypes=(("Video Files", "*.mp4"),))
        entry_file.delete(0, tk.END)
        entry_file.insert(0, filepath)

    # Button to trigger the file browsing function
    browse_button = tk.Button(root, text="Browse", command=browse_file)
    browse_button.pack(side=tk.LEFT, pady=5)  # Add padding around the button

    # Button to load the video file and close the file selection window
    def on_load():
        if entry_file.get():  # Ensure something is entered
            root.video_path = entry_file.get()
            root.quit()  # Close the window

    load_button = tk.Button(root, text="Load", command=on_load)
    load_button.pack(padx=10, pady=5)  # Add padding around the load button

    root.mainloop()
    return root.video_path if hasattr(root, 'video_path') else None


def start_loading_screen(root):
    # Set the window size
    window_width = 300
    window_height = 100
    root.geometry(f'{window_width}x{window_height}')  # Set a fixed window size

    # Set up the loading label
    loading_label = tk.Label(root, text="Processing", font=("Helvetica", 16))
    loading_label.pack(expand=True, fill=tk.BOTH)  # Center the label horizontally and vertically in the window

    # Function to update the loading text
    def update_loading_text(count=0):
        count = (count + 1) % 4  # Cycle count from 0 to 3
        loading_text = "Processing" + "." * count
        loading_label.config(text=loading_text)
        root.after(500, update_loading_text, count)

    update_loading_text()  # Start the animation


def stop_loading_screen(root):
    root.destroy()
