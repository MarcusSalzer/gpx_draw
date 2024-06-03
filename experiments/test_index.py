import app_functions.data_functions as dataf
import os
from timeit import timeit

ACT_DIR = os.path.join("data", "activities_small")
index_path = os.path.join("data", "activity_index.json")

# act_index = dataf.index_activities(ACT_DIR, None, verbose=False)
# dataf.save_json(index_path, act_index)

act_index = dataf.load_act_index(index_path)
acts = act_index["activities"]

print("\n".join(dataf.check_index(act_index)))

a0 = list(acts.values())[0]
a1 = list(acts.values())[1]


print(timeit(lambda: a0 == a1, number=100))



print(timeit(lambda: dataf.find_duplicates(acts), number=1000))
