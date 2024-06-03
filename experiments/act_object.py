from app_functions.Act import Act

from app_functions import data_functions as dataf
import os

act_dir = "data_test"

file = "10022032783.fit.gz"
p, sp = dataf.load_fit(os.path.join(act_dir, file))
act = Act("TEST", points=p, sport=sp["sport_main"])

dataf.save_json(filepath=os.path.join(act_dir, "10022032783.json"), obj=act.to_dict())
dataf.save_json_gz(
    filepath=os.path.join(act_dir, "10022032783.json.gz"), obj=act.to_dict()
)

loaded = dataf.load_json(filepath=os.path.join(act_dir, "10022032783.json.gz"))

act_loaded = Act.from_dict(loaded)

print(act.points)

