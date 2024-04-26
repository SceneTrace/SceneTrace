import time

import numpy as np

from src.db import vector_client as vc
from src.db import audio_client as ac
from src.preprocessing import feature_extraction as fe
from src.preprocessing import audio_feature_extraction as afe
from src.constants import OUTPUT_DIR
import pandas as pd
import json
import os
from scipy import stats


def load_vectors(csv_file):
    df = pd.read_csv(csv_file)
    df["embedding"] = df["embedding"].astype(str)
    res = []
    for i in df["embedding"]:
        sd = json.loads(i)
        res.append(sd)
    temp_df = pd.DataFrame()
    temp_df["embedding"] = res
    df["embedding"] = temp_df["embedding"]
    vc.createTable(df["embedding"].size())
    vc.insertEmbedding(df)


def search_video(video_file):
    start = time.time()
    features = fe.compute_features(video_file, block_size=4)
    embeddings = features["embedding"]
    vector_detected_video = vc.get_video_name(embeddings)
    print("Detected video for {} : {}".format(video_file, vector_detected_video))
    end = time.time()
    print(f"Time taken to search video {video_file}: {end - start} seconds")
    return vector_detected_video

def search_audio(video_file):
    start = time.time()
    features = afe.compute_features(video_file)
    embeddings = features["embedding"]
    result = []
    res_mode = []
    for i, embedding in enumerate(embeddings):
        vector_detected_video = ac.get_top3_similar_docs(embedding)
        print("Detected video for {} : {}".format(video_file, vector_detected_video))
        frame_detected = vector_detected_video[0][2] - i
        res_mode.append(frame_detected)
        result.append(vector_detected_video)
    end = time.time()
    mode, count = stats.mode(np.array(res_mode))
    print(f"starting frame is : {mode}")
    print(f"Time taken to search video {video_file}: {end - start} seconds")
    return result


def extract_features(video_file, store=False):
    features = fe.compute_features(video_file)
    vc.createTable(features["embedding"][0].size())
    vc.insertEmbedding(features)
    output_file = os.path.join(OUTPUT_DIR, "feature_vectors_{}.csv".format(os.path.basename(video_file).split('.')[0]))
    if store:
        features.to_csv(output_file, index=False)


def extract_audio_features(video_file, store=False):
    features = afe.compute_features(video_file)
    ac.createTable()
    ac.insertEmbedding(features)
    # ac.createIndex()
    output_file = os.path.join(OUTPUT_DIR, "feature_vectors_{}.csv".format(os.path.basename(video_file).split('.')[0]))
    if store:
        features.to_csv(output_file, index=False)

