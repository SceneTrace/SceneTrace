from src.db import *
import pandas as pd
import json

def migrate():
    createTable()
    df = pd.read_csv("feature_vectors.csv")
    df["embedding"] = df["embedding"].astype(str)
    res = []
    for i in df["embedding"]:
        sd = json.loads(i)
        res.append(sd)
    temp_df = pd.DataFrame()
    temp_df["embedding"] = res
    df["embedding"] = temp_df["embedding"]
    insertEmbedding(df)
    createIndex(df)
