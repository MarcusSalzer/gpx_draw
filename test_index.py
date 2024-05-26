import data_functions as dataf
import os

ACT_DIR = os.path.join("data", "activities")
act_index = dataf.index_activities(ACT_DIR, None, verbose=False)

index_path = os.path.join("data", "activity_index.json")

dataf.save_act_index(index_path, act_index)

print("saved index!")

print("===")
print(act_index)
