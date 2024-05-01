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
    return vlc_instance


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


def create_media_player(vlc_instance, filepath, start_frame=0):
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(filepath)
    player.set_media(media)

    # Set the start frame
    media.add_option(f'start-time={int(start_frame / constants.FPS)}')  # Convert milliseconds to seconds

    return player


def setup_window(player, video_canvas):
    if platform == "win32":
        video_canvas.winfo_toplevel().state('zoomed')
        player.set_hwnd(video_canvas.winfo_id())
    elif platform == "darwin":
        video_canvas.winfo_toplevel().tk.call("wm", "attributes", ".", "-zoomed", "1")
        player.set_nsobject(video_canvas.winfo_id())
    else:
        video_canvas.winfo_toplevel().attributes('-zoomed', True)
        player.set_xwindow(video_canvas.winfo_id())


def play_video(vlc_instance, filepath, start_frame=0, processing_time=30, callback=None):
    def configure_style():
        style = ttk.Style()
        style.configure('Info.TLabel', font=('Helvetica', 12), anchor="w")  # Increased font and left-align
        style.configure('Info.TButton', font=('Helvetica', 10))  # Increased font for buttons

    def update_progress():
        if player.is_playing():
            length = player.get_length()
            time = player.get_time()
            if length > 0:
                percentage = int((time / length) * 100)
                progress['value'] = percentage
        video_window.after(1000, lambda: update_progress())

    def close_player(new_query=False):
        player.stop()
        video_window.destroy()
        if callback:
            callback(new_query)

    def toggle_play_pause():
        if player.is_playing():
            player.pause()
            toggle_button.config(image=play_image)
        else:
            player.play()
            toggle_button.config(image=pause_image)

    def stop_video():
        player.stop()
        toggle_button.config(image=play_image)

    video_window = tk.Tk()
    video_window.title("Video Player")
    configure_style()  # Apply the style configuration

    player = create_media_player(vlc_instance, filepath, start_frame)
    video_canvas = tk.Canvas(video_window, bg='black', height=720, width=1280)  # 16:9 aspect ratio
    video_canvas.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="nsew")  # Add padding
    setup_window(player, video_canvas)

    # Info and button frame
    info_frame = tk.Frame(video_window)
    info_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=300, sticky="nsew")

    # Labels with left alignment and larger fonts
    tk.Label(info_frame, text=f"Video: {os.path.basename(filepath)}", anchor='w', font=('Helvetica', 12)).pack(fill='x')
    tk.Label(info_frame, text=f"Start Frame: {start_frame}", anchor='w', font=('Helvetica', 12)).pack(fill='x')
    tk.Label(info_frame, text=f"Processing Time: {processing_time:0.03f}s", anchor='w', font=('Helvetica', 12)).pack(
        fill='x')

    button_frame = tk.Frame(info_frame)
    button_frame.pack(pady=10, anchor='w')

    # Buttons with larger fonts
    new_query_button = ttk.Button(button_frame, text="New Query", command=lambda: close_player(True),
                                  style='Info.TButton')
    new_query_button.pack(side=tk.LEFT, padx=10)

    exit_button = ttk.Button(button_frame, text="Exit", command=lambda: close_player(False), style='Info.TButton')
    exit_button.pack(side=tk.LEFT, padx=10)

    # Control frame with buttons and progress bar
    control_frame = tk.Frame(video_window)
    control_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=20, pady=10)

    res_path = os.path.join(os.path.dirname(__file__), "res")
    play_image = tk.PhotoImage(file=os.path.join(res_path, "play.png"))
    pause_image = tk.PhotoImage(file=os.path.join(res_path, "pause.png"))
    stop_image = tk.PhotoImage(file=os.path.join(res_path, "stop.png"))
    toggle_button = tk.Button(control_frame, image=pause_image,
                              command=lambda: toggle_play_pause())
    toggle_button.pack(side=tk.LEFT, padx=10)

    tk.Button(control_frame, image=stop_image, command=lambda: stop_video()).pack(side=tk.LEFT,
                                                                                  padx=10)

    progress = ttk.Progressbar(control_frame, length=1180, mode='determinate')  # Adjust length
    progress.pack(side=tk.LEFT, padx=10, fill=tk.X)

    update_progress()

    toggle_button.config(image=play_image)  # Initially set to "Pause" since the video starts playing

    video_window.mainloop()
