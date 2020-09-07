import os
from shutil import copyfile

with open("new_csv.txt") as f:
    for l in f.readlines():
        filename = os.path.join(
            "/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/new_csvs",
            l.replace("Only in new_csvs: ", "").strip(),
        )
        copyfile(filename,
                 f"/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/csvs_not_in_dlcs/{l.replace('Only in new_csvs: ', '').strip()}")

