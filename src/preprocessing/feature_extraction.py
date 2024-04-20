import cv2
import os
import numpy as np
import librosa
import pandas as pd
from src.constants import ROOT_PATH
from src.preprocessing.utils import calculate_variance, extract_i_frames, process_audio_from_video, find_dominant_colors


def extract_freq_vectors(img, block_size=8):
    # Convert image to YCrCb and extract the Y channel
    img_y = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)[:, :, 0]

    h, w = img_y.shape
    h = h - (h % block_size)
    w = w - (w % block_size)
    img_y = img_y[:h, :w]

    # Initialize lists to store DC and AC coefficients
    dc_coefficients = []
    # ac_coefficients = []

    # Process each 8x8 block
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = img_y[i:i + block_size, j:j + block_size]
            dct_block = cv2.dct(np.float32(block))
            dc_coefficients.append(dct_block[0, 0])
            # acs = dct_block.flatten()[1:]
            # ac_coefficients.append(acs)
    return dc_coefficients


def extract_color_features(image):
    frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    dominant_colors = find_dominant_colors(frame, k=5)
    variance = calculate_variance(frame)
    dom = dominant_colors.flatten()
    return np.concatenate((dom, variance), axis=0)


def extract_audio_features(video_path, start_time_sec, end_time_sec=None):
    """
    Extracts the following audio features from a WAV file between the given start and end times in seconds:
    - Max amplitude
    - Max frequency
    - Min amplitude
    - Min frequency
    - MFCC mean
    - MFCC standard deviation
    - Audio activity threshold

    Parameters:
    video_path (str): Path to the video file (mp4 format).
    start_time_sec (float): The start time in seconds.
    end_time_sec (float): The end time in seconds. If not provided, extracts features until the end of the WAV file.

    Returns:
    numpy.ndarray: A 1D numpy array containing the requested audio features.
    """
    # Get audio file path
    audio_file_path = f'{ROOT_PATH}/Audios/{video_path.split("/")[-1].replace(".mp4", ".wav")}'

    # Load the audio file with a sampling rate of 44.1 kHz
    audio_time_series, sr = librosa.load(audio_file_path, sr=44100, mono=True)

    # Get the video frame rate (fps)
    fps = 30

    # Calculate the frame duration and hop length based on the frame rate
    frame_duration = 1 / fps
    hop_length = int(frame_duration * sr / 2)

    # Convert start time to sample index
    start_sample_idx = int(start_time_sec * sr)

    # If end time is not provided, use the end of the WAV file
    if end_time_sec is None:
        end_sample_idx = len(audio_time_series)
    else:
        end_sample_idx = int(end_time_sec * sr)

    # Extract the audio segment
    audio_segment = audio_time_series[start_sample_idx:end_sample_idx]

    # Get the MFCC features
    mfcc_features = librosa.feature.mfcc(y=audio_segment, sr=sr, hop_length=hop_length)

    # Compute MFCC statistics
    mfcc_mean = np.mean(mfcc_features, axis=1)
    mfcc_std = np.std(mfcc_features, axis=1)
    mfcc_threshold = mfcc_mean - mfcc_std

    # Compute audio activity and energy
    audio_activity = np.where(mfcc_features > mfcc_threshold[:, None], 1, 0)
    audio_energy = np.sum(audio_activity, axis=1)

    # Extract the requested features
    max_amplitude = np.max(audio_segment)
    max_frequency = np.max(librosa.fft_frequencies(sr=sr, n_fft=len(audio_segment)))
    min_amplitude = np.min(audio_segment)
    min_frequency = np.min(librosa.fft_frequencies(sr=sr, n_fft=len(audio_segment)))

    return np.array([max_amplitude, max_frequency, min_amplitude, min_frequency, np.mean(mfcc_mean), np.mean(mfcc_std),
                     np.mean(mfcc_threshold)])


def compute_features(video_file):
    video_name = os.path.basename(video_file)
    i_frames = extract_i_frames(video_file)
    vectors = []

    audio_file_path = f'{ROOT_PATH}/Audios/{video_name.replace(".mp4", ".wav")}'
    if not os.path.exists(audio_file_path):
        process_audio_from_video(video_file, audio_file_path)

    for frame in i_frames:
        image = frame['image']
        start_timestamp = frame['start_timestamp']
        end_timestamp = frame['end_timestamp']
        freq_vector = extract_freq_vectors(image, block_size=8)
        frame_id = frame['id']
        color_vectors = extract_color_features(image)
        audio_vectors = extract_audio_features(video_name, start_timestamp, end_timestamp)
        embed = list(np.concatenate((freq_vector, color_vectors, audio_vectors), axis=0))
        vectors.append([video_name, start_timestamp, frame_id, embed, True])
    pandas_df = pd.DataFrame(vectors, columns=['video_name', 'time_stamp', 'frame_num', 'embedding', 'isIFrame'])
    return pandas_df
