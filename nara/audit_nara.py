import os
import csv
import glob
import errno
import httplib2
import requests
import time

h = httplib2.Http('.cache')


def audit_images_csv():
    csvs = glob.glob("/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/ratified-indian-treaties_*.csv")

    images = []
    for csv_file in csvs:
        print(csv_file)
        with open(csv_file, "r") as f:
            csv_doc = csv.DictReader(f)
            for row in csv_doc:
                image = row["Origin"]
                images.append(image)

    return len(images)


def unredirect(uri, number_redirects=5):
    count = 1
    response, _ = h.request(uri, method="OPTIONS")
    print(response)
    location = response.get("location")
    if location:
        while location != uri and int(response.get("status")[0]) in [2, 3] and count < number_redirects:
            response, _ = h.request(location, method="OPTIONS")
            if response.get("location"):
                location = response.get("location")
            count += 1
    return location


def unredirect_requests(uri, number_redirects=5):
    count = 1
    response = requests.options(uri)
    print(response.headers)
    location = response.headers.get("location")
    print(location)
    if location:
        while location != uri and int(str(response.status_code)[0]) in [2, 3] and count < number_redirects:
            print("Trying redirect")
            response = requests.options(location)
            if response.headers.get("location"):
                location = response.headers.get("location")
            count += 1
    # else:
    #     time.sleep(2)
    #     location = unredirect_requests(uri=uri)
    return location


print(unredirect_requests("https://catalog.archives.gov/catalogmedia/lz/dc-metro/rg-011/299798/86852369/86852369-001_ac.jpg"))
