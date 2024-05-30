import numpy as np
import data_functions as dataf
import os
from timeit import timeit

activities = dataf.load_all_gpx("data/activities", sample=1)

act = dataf.Act.from_gpxpy(activities[0])
print(act)
print(act.points.dtypes)