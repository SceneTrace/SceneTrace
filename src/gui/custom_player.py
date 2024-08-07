import math

import vlc
from sys import platform
from src.constants import FPS, SEEK_SECONDS


class CustomVideoPlayer:
    def __init__(self, vlc_instance, filepath, video_canvas, start_frame=0):
        self.filepath = filepath
        self.video_canvas = video_canvas
        self.start_frame = start_frame
        self.vlc_instance = vlc_instance
        self.player = self.create_media_player()

    @staticmethod
    def setup_vlc_instance():
        """Sets up VLC options and returns a new VLC instance."""
        options = [
            '--no-xlib',  # This tells VLC not to use Xlib for video output, which can disable VAAPI
            '--avcodec-hw=none',  # Explicitly disable any hardware decoding
        ]
        return vlc.Instance(options)

    def create_media_player(self):
        """Creates a VLC media player with the provided video file."""
        player = self.vlc_instance.media_player_new()
        media = self.vlc_instance.media_new(self.filepath)

        # Set the start frame
        media.add_option(f'start-time={math.floor(self.start_frame / FPS)}')

        player.set_media(media)
        return player

    def setup_window(self):
        """Assigns the video output to the correct system interface based on the operating system."""
        if platform == "win32":
            self.player.set_hwnd(self.video_canvas.winfo_id())
        elif platform == "darwin":
            self.player.set_nsobject(self.video_canvas.winfo_id())
        else:
            self.player.set_xwindow(self.video_canvas.winfo_id())

    def play(self):
        """Starts or resumes playing the video."""
        self.player.play()

    def pause(self):
        """Pauses the video playback."""
        self.player.pause()

    def stop(self):
        """Stops the video playback and resets the player."""
        self.player.stop()

    def release(self):
        """Releases the player resources."""
        self.player.release()

    def seek(self, forward=True):
        """Seeks the video forward or backward by a given number of seconds."""
        if self.player.is_playing():
            # Calculate the seek time based on direction
            seek_time = (SEEK_SECONDS if forward else -SEEK_SECONDS) * 1000
            current_time = self.player.get_time() + seek_time
            self.player.set_time(current_time)

    def change_playback_speed(self, speed):
        """Changes the playback speed of the video."""
        self.player.set_rate(float(speed))

    def is_playing(self):
        """Checks if the video is currently playing."""
        return self.player.is_playing()

    def get_time(self):
        """Returns the current playback time in milliseconds."""
        return self.player.get_time()

    def get_length(self):
        """Returns the length of the video in milliseconds."""
        return self.player.get_length()

    def update_progress(self, progress_widget):
        """Updates the given progress widget based on the current playback state."""
        if self.is_playing():
            length = self.get_length()
            current_time = self.get_time()
            if length > 0:
                percentage = int((current_time / length) * 100)
                progress_widget['value'] = percentage
