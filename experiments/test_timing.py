from app_functions import data_functions as dataf
import os
from timeit import timeit

act_dir = "data/activities"
t = "10022032783.fit.gz"
t = "10022032783.fit"

def load_fit():
    return dataf.load_fit(os.path.join(act_dir, t))


print(load_fit())
print(timeit(lambda: load_fit(), number=1))
