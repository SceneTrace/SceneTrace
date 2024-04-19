import json
import pandas as pd
from migration import *
from db import *

if __name__ == '__main__':
    df = pd.read_csv("feature_vectors_output.csv")
    df["embedding"] = df["embedding"].astype(str)
    res = []
    for i in df["embedding"]:
        sd = json.loads(i)
        res.append(sd)
    temp_df = pd.DataFrame()
    temp_df["embedding"] = res
    df["embedding"] = temp_df["embedding"]
    name = get_video_name(df["embedding"])
    for i, embedding in enumerate(df["embedding"]):
        print("top 3 for this input : ", df["video_name"][i], df["frame_num"][i])
        print("result : ", get_top3_similar_docs(embedding, name))


    #
    # df = pd.DataFrame()
    # for i in range(1, 6):
    #     df = df._append(create_df("feature_vectors_video{}.mp4.csv".format(i)), ignore_index=True)
    # df = df._append(create_df("feature_vectors.csv"), ignore_index=True)
    # migrate(df)


