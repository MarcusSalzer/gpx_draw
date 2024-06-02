from app_functions import data_functions as dataf
import os

act_dir = "data/activities"
t = "10022032783.fit.gz"

print()
print(os.listdir(act_dir))

print(dataf.unzip_gz(act_dir, t))

t = dataf.load_fit(os.path.join(act_dir, t[:-3]))
print(t)
