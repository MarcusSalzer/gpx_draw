from app_functions import data_functions as dataf
from app_functions.activity import Act
import os
from timeit import timeit

act_dir = "data_test"
# t = "10022032783.fit"

act_dict = dataf.load_json(os.path.join(act_dir, "10022032783.json.gz"))


def load_fit():
    return dataf.load_fit(os.path.join(act_dir, "10022032783.fit.gz"))


def load_json_act(f):
    return dataf.load_json(os.path.join(act_dir, f))

def dict_to_act(d):
    return Act.from_dict(d)

N_test = 100
print(
    f"{'load json':20s}",
    timeit(lambda: load_json_act("10022032783.json"), number=N_test) / N_test,
)
print(
    f"{'load json gz':20s}",
    timeit(lambda: load_json_act("10022032783.json.gz"), number=N_test) / N_test,
)
print(
    f"{'convert to act':20s}",
    timeit(lambda: dict_to_act(act_dict), number=N_test) / N_test,
)

# print(load_json_act())
