from data_functions import index_activities
from timeit import timeit
import os

ACT_DIR = os.path.join("data", "activities")
act_index = index_activities(ACT_DIR,None,verbose=True)

print("===")
print(act_index)
