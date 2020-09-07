import json
import requests
import glob
import time

json_files = glob.glob("/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/json_not_in_dlcs/*.json")

for j in json_files[300:]:
    print(j)
    with open(j, "r") as f:
        data = json.load(f)
        if data:
            r = requests.post("https://api.dlcs-ida.org/customers/2/queue",
                              json=data,
                              auth=("a39e04ce-5653-4298-b64f-126db1b0ef3c",
                                    "f1393391845cc3da8f9e387157f00117bad235765b64539587734541d85eedba"))
            if r.status_code != 201:
                print("Erk", j)
            else:
                print(".")
        time.sleep(2)

