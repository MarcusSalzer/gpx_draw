from data_functions import index_activities
from timeit import timeit
import os
import json

ACT_DIR = os.path.join("data", "activities")
act_index = index_activities(ACT_DIR, None, verbose=False)

with open(os.path.join("data","activity_index.json"),"w") as f:
    json.dump(act_index,f)
    print("saved index!")

print("===")
print(act_index)
