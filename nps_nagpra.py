import requests
from bs4 import BeautifulSoup
import os
from docx.api import Document
import glob
import subprocess
import json
import csv
import codecs


def get_source(uri):
    r = requests.get(uri)
    if r.status_code == requests.codes.ok:
        source = r.content
        return source
    else:
        return


def get_links(doc, base):
    soup = BeautifulSoup(doc, features="lxml")
    links = ["".join([base, link['href']]) for link in soup.find_all('a', href=True)]
    return links


def filter_links(links, filter_str):
    return [link for link in links if filter_str in link]


def fetch(url_list, destination):
    for url in url_list:
        filename = url.split("/")[-1]
        destination_file = os.path.join(destination, filename)
        print(destination_file)
        r = requests.get(url, allow_redirects=True)
        with open(destination_file, "wb") as f:
            f.write(r.content)


def convert_to_docx(word_doc):
    # doc = Document(word_doc)
    subprocess.call(['/Applications/LibreOffice.app/Contents/MacOS/soffice',
                     '--headless', '--convert-to', 'docx', word_doc])


def convert_to_csv(word_doc):
    # doc = Document(word_doc)
    subprocess.call(['python',
                     'bin/docx2csv', '--format', 'csv', word_doc])


def normalize_csv(csv_file):
    print(csv_file)
    with codecs.open(csv_file, "r", encoding="utf-8") as f:
        c = csv.DictReader(f)
        rows = []
        for row in c:
            print(row)
            row_dict = {k[2:-1]:v[2:-1] for k, v in row.items()}
            rows.append(row_dict)
        # print(rows[0])
        fieldnames = [k for k, _ in rows[0].items()]
        headers = {n:n for n in fieldnames}
        with open(csv_file.replace("_1.csv", "_2.csv"), "w") as f_out:
            dw = csv.DictWriter(f_out, fieldnames=fieldnames)
            dw.writerow(headers)
            for crow in rows:
                dw.writerow(crow)
        # print(json.dumps(rows, indent=4))


def iter_visual_cells(row):
    """
    https://github.com/python-openxml/python-docx/issues/344#issuecomment-271390490

    :param row:
    :return:
    """
    prior_tc = None
    for cell in row.cells:
        this_tc = cell._tc
        if this_tc is prior_tc:  # skip cells pointing to same `<w:tc>` element
            continue
        yield cell
        prior_tc = this_tc


def tabulate(word_doc):
    print(word_doc)
    doc = Document(word_doc)
    table = doc.tables[0]
    keys = ['MAP #', 'MAP Name', 'State', 'County', 'Tribe Named in Treaty', 'Present-Day Tribe']
    big_list = []
    for row in table.rows[1:]:
        big_list.extend([cell.text for cell in iter_visual_cells(row)])
    final = []
    for i, x in enumerate(big_list):
        if all([s.isdigit() for s in x.strip()]) and x is not '':
            final.append(dict(zip(keys, big_list[i:i + 6])))
    with open(word_doc.replace(".docx", ".json"), "w") as fout:
        json.dump(final, fout, indent=4)



if __name__ == "__main__":
    docs = glob.glob("/Volumes/Seagate Expansion "
                     "Drive/Github/ida-treaty-explorer-data/nps_docs/*.docx")
    for doc in docs:
        tabulate(doc)



