from app_functions import data_functions as dataf
import os
from timeit import timeit

act_dir = "data_test"
t = "10022032783.fit.gz"
# t = "10022032783.fit"


def load_fit():
    return dataf.load_fit(os.path.join(act_dir, t))


def load_json_act():
    return dataf.load_json(os.path.join(act_dir, "10022032783.json.gz"))


N_test = 10
print(timeit(lambda: load_json_act(), number=N_test) / N_test)

# print(load_json_act())

