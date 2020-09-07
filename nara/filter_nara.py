import json
import glob
import shutil




def identify_candidates():
    done = [
        "12013184",
        "120091472",
        "120090431",
        "120090423",
        "120090434",
        "119654273",
        "119654300",
        "119654537",
        "119866704",
        "120091455",
        "58234673",
        "60595667",
        "60677736",
        "60630177",
        "60646161",
        "60582354",
        "60675424",
        "60659853",
        "60664580",
        "60679874",
        "60667718",
        "58328187",
    ]
    csvs = glob.glob("/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/*.csv")
    csv_tuples = list(set([(x.split("_")[1].split(".csv")[0], x) for x in csvs]))
    filtered = [c for c in csv_tuples if not c[0] in done]
    for id, filename in filtered:
        print(filename)
        new_filename = filename.replace("/nara/", "/filtered_nara/")
        print(new_filename)
        dest = shutil.copyfile(filename, new_filename)


identify_candidates()

