import json
import os
import dateparser
import datetime
import en_core_web_sm
import csv
import uuid


def summarise(record):
    lists = {}
    strings = {}
    dicts = {}
    for k, v in record.items():
        if type(v) == list:
            if not lists.get(k):
                lists[k] = {"length": 0}
                if len(v) > lists[k]["length"]:
                    lists[k]["length"] = len(v)
            else:
                if len(v) > lists[k]["length"]:
                    lists[k]["length"] = len(v)
        elif type(v) == str:
            if not strings.get(k):
                strings[k] = {"values": []}
        elif type(v) == dict:
            dicts[k] = summarise(v)
    return {"strings": strings, "lists": lists, "dicts": dicts}


def survey(nara_file=None):
    """
    Generate a summary of the data structure.

    :param nara_file:
    :return:
    """
    if not nara_file:
        nara_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "nara-export-latest.json")
        )
    with open(nara_file, "r") as f:
        nara_json = json.load(f)
    lists = {}
    strings = {}
    dicts = {}
    digitised = []
    for record in nara_json:
        # if record.get("documentIndex") == 228:
        for k, v in record.items():
            # print(k)
            # print(type(v))
            if type(v) == list:
                if not lists.get(k):
                    lists[k] = {"length": 0, "values": []}
                    if len(v) > lists[k]["length"]:
                        lists[k]["length"] = len(v)
                    for x in v:
                        if type(x) != dict:
                            lists[k]["values"].append(x)
                        else:
                            lists[k]["values"].append(json.dumps(x))
                else:
                    if len(v) > lists[k]["length"]:
                        lists[k]["length"] = len(v)
                    for x in v:
                        if type(x) != dict:
                            lists[k]["values"].append(x)
                        else:
                            lists[k]["values"].append(json.dumps(x))
                lists[k]["values"] = list(set(lists[k]["values"]))
            elif type(v) == str:
                if not strings.get(k):
                    strings[k] = {"values": []}
                    strings[k]["values"].append(v)
                else:
                    strings[k]["values"].append(v)
                strings[k]["values"] = list(set(strings[k]["values"]))
            elif type(v) == dict:
                dicts[k] = summarise(v)
        if record.get("objects"):
            digitised.append(
                {
                    "documentIndex": record.get("documentIndex"),
                    "title": record.get("title"),
                    "url": record.get("url"),
                    "date": record.get("productionDates"),
                }
            )
    summary = {"strings": strings, "lists": lists, "dicts": dicts}
    nara_summary = os.path.abspath(os.path.join(os.path.dirname(__file__), "nara-summary.json"))
    nara_digitised = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "nara-digitised.json")
    )
    with open(nara_summary, "w") as f:
        json.dump(summary, f, indent=4, sort_keys=True)
    with open(nara_digitised, "w") as d:
        json.dump(digitised, d, indent=4, sort_keys=True)
    print(len(digitised))


def run(nara_file=None):
    """
    Insert the data into the model

    :param nara_file:
    :return:
    """
    nlp = en_core_web_sm.load()
    if not nara_file:
        nara_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "nara-export-latest.json")
        )
    with open(nara_file, "r") as f:
        nara_json = json.load(f)
    for record in nara_json:
        r = dict(
            title=record.get("title").strip(),
            catalogue_url=record.get("url"),
            na_id=record.get("naId"),
            restrictions=record.get("useRestrictions")[0],
            arc_identifier=record.get("arcIdentifier"),
            date_note=record.get("dateNote"),
        )
        level = record.get("levelOfDescription")
        if record.get("otherTitles"):
            r["other_titles"] = [x.strip() for x in record.get("otherTitles")]
        if record.get("generalNotes"):
            r["general_notes"] = [x.strip() for x in record.get("generalNotes")]
        if record.get("scopeAndContentNote"):
            r["content_note"] = record.get("scopeAndContentNote").strip()
        if level == "Item":
            r["level_of_description"] = "I"
        else:
            r["level_of_description"] = "F"
        if record.get("objects"):
            r["digitised"] = True
        start_date = None
        end_date = None
        r["other_dates"] = []
        if record.get("productionDates"):
            d = record.get("productionDates")
            if d:
                r["production_date_string"] = d[0]
                if len(d[0]) == 4:
                    # if it's a year, make the range the whole year
                    start_date = datetime.datetime(int(d[0]), 1, 1)
                    end_date = datetime.datetime(int(d[0]) + 1, 1, 1)
                else:
                    # just make the start and end of the range the same date
                    start_date = dateparser.parse(d[0])
                    end_date = start_date
                r["start_date"] = f"{start_date}"
                r["end_date"] = f"{end_date}"
        doc = nlp(r["title"])
        for ent in doc.ents:
            if ent.label_ == "DATE":
                r["other_dates"].append(f"{dateparser.parse(ent.text)}")
        print(json.dumps(r, indent=4))


def run_iiif(nara_file):
    if not nara_file:
        nara_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "nara-export-latest.json")
        )
    with open(nara_file, "r") as f:
        nara_json = json.load(f)
    digitised_objects = []
    for record in nara_json:
        r = dict(arc_id=record.get("arcIdentifier"), title=record.get("title"))
        if record.get("objects"):
            objects = record.get("objects")
            item_objects = objects["object"]
            r["jpegs"] = [
                x["file"]["@url"]
                for x in item_objects
                if ".jpg" in x["file"]["@url"].lower()
                and "thumb" not in x["file"]["@url"].lower()
                and ".tif" not in x["file"]["@url"].lower()
            ]
            r["gifs"] = [
                x["file"]["@url"]
                for x in item_objects
                if ".gif" in x["file"]["@url"].lower() and "thumb" not in x["file"]["@url"].lower()
            ]
            # if r["arc_id"] == "299799":
            #     print(json.dumps(item_objects, indent=2))
            digitised_objects.append(r)
    return digitised_objects


def gen_csvs(digitised):
    for d in digitised:
        # print(json.dumps(d, indent=3))
        series = "ratified-indian-treaties"
        origins = []
        if len(d["jpegs"]) > 0:
            for c, j in enumerate(d["jpegs"]):
                number_reference = None
                url = j.lower().replace(
                    "https://catalog.archives.gov/catalogmedia",
                    "https://s3.amazonaws.com/NARAprodstorage",
                )
                if "_ac.jpg" in j:
                    number_reference = url.replace("_ac.jpg", "").split("-")[-1]
                elif "-ac.jpg" in j:
                    number_reference = url.replace("-ac.jpg", "").split("-")[-1]
                elif "AC.jpg" in j:
                    number_reference = url.replace("_ac.jpg", "").split("_")[-1]
                elif "PR.jpg" in j:
                    number_reference = url.replace("_pr.jpg", "").split("_")[-1]
                if number_reference:
                    origins.append(
                        {
                            "Origin": j,
                            "NumberReference1": int(number_reference),
                            "Reference1": series,
                            "Reference2": d["arc_id"],
                            "ID": str(uuid.uuid4()),
                            "Space": 1,
                            "Line": int(c),
                            "Type": "Image",
                            "MaxUnauthorised": -1,
                        }
                    )
            origins.sort(key=lambda result: result["Line"])
            print(origins)
            members = [
                    {
                        "space": 1,
                        "origin": o["Origin"].replace("https://catalog.archives.gov/catalogmedia",
                                                      "https://s3.amazonaws.com/NARAprodstorage"),
                        "string1": o["Reference1"],
                        "string2": o["Reference2"],
                        "number1": o["NumberReference1"],
                    }
                    for o in origins
                ]
            new_origins = {
                "@type": "Collection",
                "member": members
            }
            print(json.dumps(origins, indent=2))
            csv_file = series + "_" + d["arc_id"] + ".csv"
            if os.path.exists(
                os.path.join(
                    "/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/csvs_not_in_dlcs/",
                    csv_file

                )
            ):
                with open(
                    os.path.join(
                        "/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/json_not_in_dlcs",
                        csv_file.replace(".csv", ".json"),
                    ),
                    "w",
                ) as jf:
                    json.dump(new_origins, jf)
            with open(csv_file, "w") as csvfile:
                fieldnames = [
                    "Type",
                    "Line",
                    "Space",
                    "ID",
                    "Origin",
                    "InitialOrigin",
                    "Reference1",
                    "Reference2",
                    "Reference3",
                    "Tags",
                    "Roles",
                    "MaxUnauthorised",
                    "NumberReference1",
                    "NumberReference2",
                    "NumberReference3",
                ]
                writer = csv.DictWriter(
                    csvfile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL
                )
                writer.writeheader()
                for origin in origins:
                    writer.writerow(origin)


gen_csvs(digitised=run_iiif(nara_file="nara-export-latest.json"))
