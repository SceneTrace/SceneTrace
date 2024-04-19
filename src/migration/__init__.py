from src.db import *
import pandas as pd
import json

def create_df(fileName):
    df = pd.read_csv(fileName)
    df["embedding"] = df["embedding"].astype(str)
    res = []
    for i in df["embedding"]:
        sd = json.loads(i)
        res.append(sd)
    temp_df = pd.DataFrame()
    temp_df["embedding"] = res
    df["embedding"] = temp_df["embedding"]
    return df

def migrate(df):
    createTable()
    insertEmbedding(df)
    createIndex(df)
