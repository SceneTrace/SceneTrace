from src.db import vector_client as vc
import pandas as pd
import json


def migrate():
    vc.createTable()
    df = pd.read_csv("feature_vectors.csv")
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

def search(embeddings):
    for i, embedding in enumerate(embeddings):
        print("top 3 for this input : ", embedding["video_name"][i], embedding["frame_num"][i])
        print("result : ", vc.get_top3_similar_docs(embedding["embedding"]))
