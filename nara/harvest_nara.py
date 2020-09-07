import os
import csv
import glob
import errno
import httplib2
import time


def audit_images_csv(glob_str):
    csvs = glob.glob(glob_str)
    images = []
    for csv_file in csvs:
        with open(csv_file, "r") as f:
            csv_doc = csv.DictReader(f)
            for row in csv_doc:
                image = row["Origin"]
                images.append(image)
    return len(images)



def unredirect(uri, h, number_redirects=5, redirected=0):
    count = 1
    response, _ = h.request(uri, method="OPTIONS")
    location = response.get("location")
    if location:
        while location != uri and int(response.get("status")[0]) in [2, 3] and count < number_redirects:
            response, _ = h.request(location, method="OPTIONS")
            if response.get("location"):
                location = response.get("location")
            count += 1
    elif response.get("status") == '200':
        return uri
    else:
        if redirected < number_redirects:
            time.sleep(2)
            location = unredirect(uri=uri, h=h, redirected=redirected + 1)
    return location


def fetch_images(glob_string, h, total):
    csvs = glob.glob(glob_string)
    progress = 0
    for csv_file in csvs:
        with open(csv_file, "r") as f:
            csv_doc = csv.DictReader(f)
            for row in csv_doc:
                progress += 1
                print(f"{progress} of {total}")
                image = row["Origin"]
                collection = row["Reference1"]
                object_id = row["Reference2"]
                filename = image.split("/")[-1]
                destination_dir = f"/Volumes/IDA2/nara/{collection}/{object_id}/"
                destination_filename = destination_dir + filename
                if os.path.exists(destination_filename):
                    size = os.path.getsize(destination_filename)
                    if size < 10000:
                        print(f"{destination_filename} exists but is too small to be valid.")
                        get = True
                    else:
                        print(f"{destination_filename} Exists and is good")
                        get = False
                else:
                    print(f"{destination_filename} does not exist.")
                    get = True
                if get:
                    try:
                        os.makedirs(destination_dir)
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
                    image_uri = unredirect(uri=image, h=h)
                    if image_uri:
                        try:
                            image_response, image_content = h.request(image_uri)
                            if image_content:
                                print(f"Writing {filename}")
                                with open(destination_filename, 'wb') as i_f:
                                    i_f.write(image_content)
                        except ConnectionResetError:
                            print(f"Connection reset on {image}")


httplib_ = httplib2.Http()

g = "/Users/matt.mcgrattan/Documents/Github/ida-treaty-explorer-data/nara/ratified-indian-treaties_*.csv"
fetch_images(glob_string=g, h=httplib_, total=audit_images_csv(glob_str=g))