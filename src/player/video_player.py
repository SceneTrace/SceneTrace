import os
from sys import platform
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
import vlc
from src import constants


def setup_player():
    # VLC options to force software decoding by specifying a video output module
    options = [
        '--no-xlib',  # This tells VLC not to use Xlib for video output, which can disable VAAPI
        '--avcodec-hw=none',  # Explicitly disable any hardware decoding
        '--vout=flaschen',  # Use software rendering
    ]
    # Create a new VLC instance with the specified options
    vlc_instance = vlc.Instance(options)
    # Create a VLC media player with this instance
    player = vlc_instance.media_player_new()
    return vlc_instance, player


def file_selection():
    # Initialize the main root window for each iteration
    root = tk.Tk()
    root.title(constants.APP_NAME)

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
    filepath = root.video_path if hasattr(root, 'video_path') else None
    root.destroy()  # Destroy the window after the loop ends
    return filepath


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


def play_video(player, vlc_instance, filepath):
    # Create a new root window for the video
    video_window = tk.Tk()
    video_window.title("Video Player")

    # Create a Canvas as a placeholder for the video
    video_canvas = tk.Canvas(video_window, bg='black')
    video_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Load the video file into the VLC player using the instance
    media = vlc_instance.media_new(filepath)
    player.set_media(media)

    # Platform-specific maximization and window identifier settings
    if platform == "win32":  # Checks for Windows
        video_window.state('zoomed')
        player.set_hwnd(video_canvas.winfo_id())  # Window identifier for Windows
    elif platform == "darwin":  # macOS
        video_window.tk.call("wm", "attributes", ".", "-zoomed", "1")
        player.set_nsobject(video_canvas.winfo_id())  # Window identifier for macOS
    else:  # Linux or Unix-like OS
        video_window.attributes('-zoomed', True)
        player.set_xwindow(video_canvas.winfo_id())  # Window identifier for Linux

    # Load control images
    res_path = os.path.join(os.path.dirname(__file__), "res")
    play_image = tk.PhotoImage(file=os.path.join(res_path, "play.png"))
    pause_image = tk.PhotoImage(file=os.path.join(res_path, "pause.png"))
    stop_image = tk.PhotoImage(file=os.path.join(res_path, "stop.png"))

    # Frame for buttons and progress bar
    control_frame = tk.Frame(video_window)
    control_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Button to toggle play and pause
    toggle_button = tk.Button(control_frame, image=pause_image, command=lambda: toggle_play_pause(), height=40, width=40)
    toggle_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Stop button
    stop_button = tk.Button(control_frame, image=stop_image, command=lambda: stop_video(), height=40, width=40)
    stop_button.pack(side=tk.LEFT, padx=5, pady=5)

    # Progress bar
    progress = ttk.Progressbar(control_frame, length=200, mode='determinate')
    progress.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

    # Function to toggle play and pause based on the player's state
    def toggle_play_pause():
        if player.is_playing():
            player.pause()
            toggle_button.config(image=play_image)  # Set button image to 'Play'
        else:
            player.play()
            toggle_button.config(image=pause_image)  # Set button image to 'Pause'

    # Function to stop the video player and close the window
    def stop_video():
        player.stop()
        video_window.destroy()

    # Function to update the progress bar
    def update_progress():
        if player.is_playing():
            # Get the length of the video in milliseconds and current position
            length = player.get_length()
            time = player.get_time()
            if length > 0:
                percentage = int((time / length) * 100)
                progress['value'] = percentage
        video_window.after(1000, update_progress)

    update_progress()

    # Initial play
    player.play()
    toggle_button.config(image=pause_image)  # Initially set to "Pause" since the video starts playing

    video_window.mainloop()
