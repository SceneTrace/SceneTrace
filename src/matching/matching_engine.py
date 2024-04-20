from src.db import vector_client as vc
from src.preprocessing import feature_extraction as fe
from src.constants import OUTPUT_DIR
import pandas as pd
import json
import os


def load_vectors(csv_file):
    vc.createTable()
    df = pd.read_csv(csv_file)
    df["embedding"] = df["embedding"].astype(str)
    res = []
    for i in df["embedding"]:
        sd = json.loads(i)
        res.append(sd)
    temp_df = pd.DataFrame()
    temp_df["embedding"] = res
    df["embedding"] = temp_df["embedding"]
    vc.insertEmbedding(df)
    vc.createIndex(df)


def search_video(video_file):
    features = fe.compute_features(video_file)
    embeddings = features["embeddings"]
    vector_detected_video = vc.get_video_name(embeddings)
    return vector_detected_video


def extract_features(video_file, store=False):
    features = fe.compute_features(video_file)
    vc.createTable()
    vc.insertEmbedding(features)
    vc.createIndex(features)
    output_file = os.path.join(OUTPUT_DIR, "feature_vectors_{}.csv".format(os.path.basename(video_file).split('.')[0]))
    if store:
        features.to_csv(output_file, index=False)

