from db import *
import pandas as pd

if __name__ == '__main__':
    createTable()
    # initialize list of lists

    data = [['sam', '10', 2, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], True],['bob', '10', 2, [123, 2, 3, 4, 12, 6, 7, 8, 9, 112, 11, 12, 13, 14, 15], True],['tom', '10', 2, [12, 2, 3, 4, 11, 6, 7, 8, 9, 10, 11, 12, 13, 17, 15], True]]
    df = pd.read_csv("nba.csv")
    insertEmbedding(df)
    createIndex(df)
    res = get_top3_similar_docs([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    print(res)


    # 288,372