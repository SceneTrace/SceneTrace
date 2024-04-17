import os
import numpy as np
import pandas as pd
from constants import ROOT_PATH
from preprocessing.feature_extraction import extract_freq_vectors, extract_color_features, extract_audio_features
from preprocessing.utils import extract_i_frames, process_audio_from_video

if __name__ == "__main__":
    i_frames = {}
    for i in range(1, 2):
        video_name = "queryvideo1.mp4"
        video_path = os.path.join(ROOT_PATH, video_name)
        i_frames[video_name] = extract_i_frames(video_path)
        vectors = []
        audio_file_path = f'{ROOT_PATH}/Audios/{video_name.replace(".mp4", ".wav")}'
        if not os.path.exists(audio_file_path):
            process_audio_from_video(video_path, audio_file_path)
        for key, value in i_frames.items():
            for frame in value:
                image = frame['image']
                start_timestamp = frame['start_timestamp']
                end_timestamp = frame['end_timestamp']
                freq_vector = extract_freq_vectors(image, block_size=8)
                frame_id = frame['id']
                color_vectors = extract_color_features(image)
                audio_vectors = extract_audio_features(key, start_timestamp, end_timestamp)
                embed = list(np.concatenate((freq_vector, color_vectors, audio_vectors), axis=0))
                vectors.append([key, start_timestamp, frame_id, embed, True])
        pandas_df = pd.DataFrame(vectors, columns=['video_name', 'time_stamp', 'frame_num', 'embedding', 'isIFrame'])
        pandas_df.to_csv('src/db/feature_vectors_{}.csv'.format(video_name), index=False)
        print("Done Processing {}".format(video_name))
