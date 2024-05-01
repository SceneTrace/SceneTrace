import argparse
from time import perf_counter

import tkinter as tk

from src.gui import gui
import os
import time

from constants import OUTPUT_DIR, APP_NAME
from matching.matching_engine import load_video_vectors, load_audio_vectors, extract_video_features, extract_audio_features, search_audio, \
    search_video
from src.db import audio_client as ac
from src.db import video_client as vc
from src.gui.custom_player import CustomVideoPlayer
from utils.file_utils import files_in_directory, fetch_files


def load(file_path):
    # Load the feature vectors
    csv_files = fetch_files(file_path, format=".csv")
    for file in csv_files:
        if "audio" in file:
            print("Loading audio features from {}".format(file))
            load_audio_vectors(file)
        else:
            print("Loading video features from {}".format(file))
            load_video_vectors(file)
    vc.createIndex()
    ac.createIndex()


def extract(file_path, store=False, video=False, audio=False):
    # Extract features from the video files
    print(" Video Features: {} ; Audio Features: {}".format(video, audio))
    video_files = files_in_directory(file_path, format=".mp4")
    for video_file in video_files:
        print("#" * 80)
        print("**** Extracting features from {}".format(video_file))
        if video:
            extract_video_features(video_file, store=store)
        if audio:
            extract_audio_features(video_file, store=store)
    if video:
        start = time.time()
        vc.createIndex()
        end = time.time()
        print("Creating index for video vectors took {} seconds".format(end - start))
    if audio:
        start = time.time()
        ac.createIndex()
        end = time.time()
        print("Creating index for audio vectors took {} seconds".format(end - start))


def search(video_file_path):
    # Search the query video in the database
    video_files = files_in_directory(video_file_path, format=".mp4")
    for video_file in video_files:
        print("#"*80)
        start = time.time()
        original_video_name = search_video(video_file)
        video_end_time = time.time()
        print("Searching video {} took {} seconds".format(video_file, video_end_time-start))
        audio_start = time.time()
        frame_num = search_audio(video_file, original_video_name)
        end = time.time()
        print("Searching audio for {} took {} seconds".format(video_file, end-audio_start))
        print("Complete Search for {} took {} seconds".format(video_file, end-start))
        print("*** VIDEO NAME: {} DETECTED : {}".format(video_file, original_video_name.replace(".", "_"+str(
            frame_num-1)+".")))


def validate_args(arguments):
    if len(arguments.inputs) < 1:
        raise ValueError("Please provide the input file path")
    if not os.path.exists(arguments.inputs[0]):
        raise ValueError("Input file path does not exist")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", type=str, required=False, help="Actions : Load, Extract, Search", default="Search")
    parser.add_argument("--output-dir", type=str, required=False, help="Name of the video file.",
                        default=OUTPUT_DIR)
    parser.add_argument("--store", action="store_true", help="store the vectors")
    parser.add_argument("--player", action="store_true", help="Play video using player")
    parser.add_argument("--video", action="store_true", help="extract video vectors")
    parser.add_argument("--audio", action="store_true", help="extract audio vectors")
    parser.add_argument('inputs', nargs='*', help='Optional list of extra arguments without tags')
    arguments = parser.parse_args()
    #validate_args(arguments)
    if arguments.store:
        if not os.path.exists(arguments.output_dir):
            os.makedirs(arguments.output_dir)
    if not arguments.video and not arguments.audio:
        arguments.video = True
        arguments.audio = True
    return arguments


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()

    if args.player:
        continue_playing = [True]


        def callback(new_query):
            continue_playing.clear()
            continue_playing.append(new_query)


        while continue_playing[0]:

            # File selection
            query_video, query_audio = gui.file_selection()
            vlc_instance = CustomVideoPlayer.setup_vlc_instance()

            if query_video and query_audio:
                # Create a new window for loading
                loading_root = tk.Tk()
                loading_root.title(APP_NAME)
                gui.start_loading_screen(loading_root)  # Start the processing text animation

                start_time = perf_counter()

                # TODO: Simulate processing, replace with search
                loading_root.after(3000, lambda: gui.stop_loading_screen(loading_root))
                loading_root.mainloop()

                # TODO: Call function to stop loading here instead, after the search is complete
                process_time = perf_counter() - start_time

                # TODO: Replace query video path and start_frame with the search result
                gui.play_video(vlc_instance=vlc_instance, filepath=query_video,
                               start_frame=16200,
                               processing_time=process_time,
                               callback=callback)
            else:
                continue_playing = False  # Exit the loop if no file is selected
    else:
        if args.action.lower() == "load":
            load(args.inputs[0])
        elif args.action.lower() == "extract":
            extract(args.inputs[0], store=args.store, video=args.video, audio=args.audio)
        elif args.action.lower() == "search":
            search(args.inputs[0])
