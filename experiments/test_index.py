import app_functions.data_functions as dataf
import os
from timeit import timeit

N_TIMEIT = 100
index_path = os.path.join("data", "activity_index.json")

act_index = dataf.load_act_index(index_path)
acts = act_index["activities"]

print("\n".join(dataf.check_index(act_index)))

t_check_dupl = timeit(lambda: dataf.find_duplicates(acts), number=N_TIMEIT) / N_TIMEIT
print(f"Checked duplictes: {1000*t_check_dupl:.3f} ms")
