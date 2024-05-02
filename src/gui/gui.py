import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from src.constants import APP_NAME, VID_WIDTH, VID_HEIGHT, FPS
from src.gui.custom_player import CustomVideoPlayer
from src.utils.time_utils import calculate_time


def file_selection():
    # Initialize the main root window for each iteration
    root = tk.Tk()
    root.title(APP_NAME)

    # Configure styles for ttk widgets
    style = ttk.Style()
    style.configure("Large.TButton", font=('Helvetica', 16))  # Define a large Button style

    # Configure the grid layout manager
    root.columnconfigure(0, weight=1)  # Allows column to expand and fill space

    # Label and entry for video file selection
    video_label = ttk.Label(root, text="Please select Query video (.mp4):", font=("Helvetica", 14))
    video_label.grid(row=0, column=0, padx=10, pady=(15, 5), sticky="w")

    video_entry = ttk.Entry(root, width=50)
    video_entry.grid(row=1, column=0, padx=10, pady=5, sticky="we")

    # Button to trigger video file browsing
    video_browse_button = ttk.Button(root, text="Browse Video", command=lambda: browse_file(video_entry, "mp4"))
    video_browse_button.grid(row=1, column=1, padx=10, pady=5, sticky="w")

    # Label and entry for audio file selection
    audio_label = ttk.Label(root, text="Please select Query audio (.wav):", font=("Helvetica", 14))
    audio_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    audio_entry = ttk.Entry(root, width=50)
    audio_entry.grid(row=3, column=0, padx=10, pady=5, sticky="we")

    # Button to trigger audio file browsing
    audio_browse_button = ttk.Button(root, text="Browse Audio", command=lambda: browse_file(audio_entry, "wav"))
    audio_browse_button.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    # Generic file browsing function
    def browse_file(entry, filetype):
        filetypes = {"mp4": ("Video Files", "*.mp4"), "wav": ("Audio Files", "*.wav")}
        filepath = filedialog.askopenfilename(filetypes=(filetypes[filetype],))
        entry.delete(0, tk.END)
        entry.insert(0, filepath)

    # Button to load the video and audio files and close the file selection window
    def on_load():
        if video_entry.get() and audio_entry.get():  # Ensure both files are selected
            root.video_path = video_entry.get()
            root.audio_path = audio_entry.get()
            root.quit()  # Close the window

    load_button = ttk.Button(root, text="Load", command=on_load, style="Large.TButton")
    load_button.grid(row=4, column=0, columnspan=2, padx=10, pady=20)

    root.mainloop()
    video_path = root.video_path if hasattr(root, 'video_path') else None
    audio_path = root.audio_path if hasattr(root, 'audio_path') else None
    root.destroy()  # Destroy the window after the loop ends
    return video_path, audio_path


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


def play_video(vlc_instance, filepath, start_frame=0, processing_time=30, callback=None):
    def configure_style():
        """Configure the style of the GUI elements."""
        style = ttk.Style()
        style.configure('Info.TLabel', font=('Helvetica', 12), anchor="w")
        style.configure('Info.TButton', font=('Helvetica', 12))
        style.configure('Flat.TButton', relief='flat', borderwidth=0, focuscolor='')
        style.configure('LargeFont.TCombobox',
                        font=('Helvetica', 14),
                        arrowsize=15,
                        padding=5)
        style.configure("Modern.Horizontal.TProgressbar", troughcolor='lightgrey',
                        bordercolor='grey', lightcolor='lightgrey', darkcolor='grey',
                        background='steelblue', thickness=5)

    def update_progress():
        """Updates the progress bar and timestamp labels."""
        if video_player.is_playing():
            length = video_player.get_length()
            time = video_player.get_time()
            if length > 0:
                percentage = int((time / length) * 100)
                progress['value'] = percentage

                # Update current timestamp label
                current_time_seconds = time // 1000
                current_minutes, current_seconds = calculate_time(current_time_seconds)
                current_timestamp_label.config(text=f"{current_minutes:02d}:{current_seconds:02d}")

        video_window.after(1000, update_progress)

    def close_player(new_query=False):
        """Stops the player and closes the window, possibly triggering a callback."""
        video_player.stop()
        video_player.release()
        video_window.destroy()
        if callback:
            callback(new_query)

    def toggle_play_pause():
        """Toggles the playback state between play and pause."""
        if video_player.is_playing():
            video_player.pause()
            toggle_button.config(image=play_image)
        else:
            video_player.play()
            toggle_button.config(image=pause_image)

    def stop_video():
        """Stops the video playback."""
        video_player.stop()
        toggle_button.config(image=play_image)

    video_window = tk.Tk()
    video_window.title(APP_NAME)
    configure_style()  # Apply the style configuration

    # Bind the window close button event to the on_closing function
    video_window.protocol("WM_DELETE_WINDOW", lambda: close_player(False))

    video_canvas = tk.Canvas(video_window, bg='black', width=VID_WIDTH, height=VID_HEIGHT)
    video_canvas.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="nsew")

    video_player = CustomVideoPlayer(vlc_instance, filepath, video_canvas, start_frame)
    video_player.setup_window()

    # Calculate start time and total length
    start_time_seconds = start_frame // FPS

    # Calculate minutes and seconds for start time and total length
    start_minutes, start_seconds = calculate_time(start_time_seconds)

    # Info and button frame
    info_frame = tk.Frame(video_window)
    info_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=150, sticky="nsew")

    ttk.Label(info_frame, text=f"Video: {os.path.basename(filepath)}", style='Info.TLabel').pack(fill='x', pady=10)
    ttk.Label(info_frame, text=f"Start Frame: {start_frame}", style='Info.TLabel').pack(fill='x', pady=10)
    ttk.Label(info_frame, text=f"Processing Time: {processing_time:0.03f}s", style='Info.TLabel').pack(fill='x',
                                                                                                       pady=10)

    button_frame = tk.Frame(info_frame)
    button_frame.pack(pady=10, anchor='w')

    new_query_button = ttk.Button(button_frame, text="New Query", command=lambda: close_player(True),
                                  style='Info.TButton')
    new_query_button.pack(side=tk.LEFT, padx=10)

    exit_button = ttk.Button(button_frame, text="Exit", command=lambda: close_player(False), style='Info.TButton')
    exit_button.pack(side=tk.LEFT, padx=10)

    control_frame = tk.Frame(video_window)
    control_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 10))

    res_path = os.path.join(os.path.dirname(__file__), "res")
    play_image = tk.PhotoImage(file=os.path.join(res_path, "play.png"))
    pause_image = tk.PhotoImage(file=os.path.join(res_path, "pause.png"))
    stop_image = tk.PhotoImage(file=os.path.join(res_path, "stop.png"))
    seek_forward_image = tk.PhotoImage(file=os.path.join(res_path, "seek_forward.png"))
    seek_backward_image = tk.PhotoImage(file=os.path.join(res_path, "seek_backward.png"))

    toggle_button = ttk.Button(control_frame, image=pause_image, command=toggle_play_pause, style='Flat.TButton')
    toggle_button.pack(side=tk.LEFT, padx=10)

    ttk.Button(control_frame, image=stop_image, command=stop_video, style='Flat.TButton').pack(side=tk.LEFT, padx=10)

    # Button for seeking backward
    seek_back_button = ttk.Button(control_frame, image=seek_backward_image, style='Flat.TButton',
                                  command=lambda: video_player.seek(forward=False))
    seek_back_button.image = seek_backward_image  # Keep a reference to prevent garbage collection
    seek_back_button.pack(side=tk.LEFT, padx=10)

    # Button for seeking forward
    seek_forward_button = ttk.Button(control_frame, image=seek_forward_image, style='Flat.TButton',
                                     command=lambda: video_player.seek(forward=True))
    seek_forward_button.image = seek_forward_image  # Keep a reference to prevent garbage collection
    seek_forward_button.pack(side=tk.LEFT, padx=10)

    # Speed selection combobox setup
    speeds = [str(x) for x in [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]]
    speed_combobox = ttk.Combobox(control_frame, values=speeds, state="readonly", style='LargeFont.TCombobox', width=5)
    speed_combobox.set("1.0")  # Set default speed to normal (1.0x)
    speed_combobox.bind("<<ComboboxSelected>>", lambda event: video_player.change_playback_speed(speed_combobox.get()))
    speed_combobox.pack(side=tk.LEFT, padx=10)

    current_timestamp_label = ttk.Label(control_frame, text=f"{start_minutes:02d}:{start_seconds:02d}", anchor="w")
    current_timestamp_label.pack(side=tk.LEFT, padx=10)

    progress = ttk.Progressbar(control_frame, style="Modern.Horizontal.TProgressbar",
                               orient="horizontal", length=400, mode='determinate', maximum=100)
    progress.pack(side=tk.LEFT, padx=10, pady=20, fill=tk.X)

    update_progress()

    toggle_button.config(image=play_image)  # Initially set to "Pause" since the video starts playing

    video_window.mainloop()
