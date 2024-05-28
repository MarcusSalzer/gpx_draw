import data_functions as dataf
import numpy as np
from timeit import timeit

act_index = dataf.load_act_index("data/activity_index.json")


print((dataf.eddington_nbr(act_index)))

print(timeit(lambda: dataf.eddington_nbr(act_index), number=1000))
