from app_functions.activity import Act

from app_functions import data_functions as dataf
import os

act_dir = "data_test"

file = "10022032783.fit.gz"
p, sp = dataf.load_fit(os.path.join(act_dir, file))
act = Act("TEST", points=p, sport=sp["sport_main"])

dataf.save_json(filepath=os.path.join(act_dir, "10022032783.json"), obj=act.to_dict())
# dataf.save_json_gz(
#     filepath=os.path.join(act_dir, "10022032783.json.gz"), obj=act.to_dict()
# )

loaded = dataf.load_json(filepath=os.path.join(act_dir, "10022032783.json"))

act_loaded = Act.from_dict(loaded)

print(act, act_loaded, sep="\n")

for s in Act.__slots__:
    if s != "points":
        print(s, getattr(act, s) == getattr(act_loaded, s))
    else:
        print(s, act.points.equals(act_loaded.points))

print("\nEQUAL OBJECTS?", act == act_loaded) 

