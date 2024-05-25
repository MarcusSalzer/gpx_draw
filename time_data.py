from timeit import timeit, default_timer
import pandas as pd
import json

with open("data/activity_index.json") as f:
    act_index = json.load(f)

print(act_index.keys())


def make_panda(index: dict):
    df = pd.DataFrame.from_dict(index["activities"], orient="index")
    return df


df = make_panda(act_index)

print(timeit(lambda: make_panda(act_index), number=10))

ts = default_timer()

df["time_start"] = pd.to_datetime(df["time_start"], format="%Y-%m-%d %H:%M:%S")
df["year"] = df["time_start"].dt.year
print(df.groupby("year").size())

print(default_timer() - ts)
