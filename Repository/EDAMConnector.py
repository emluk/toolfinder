import csv
import json
from io import StringIO
import requests


base_url = "https://edamontology.org"


def load():
    print("Retrieving EDAM ontology definition...", end=" ")
    response = requests.get(f"{base_url}/EDAM.csv")
    if response.status_code != 200:
        print(f'Failed to get EDAM definition from {base_url}/EDAM.csv')
        return
    edam_dict = {}
    csv_data = StringIO(response.content.decode('utf-8').replace("\r\n", "\n"))
    reader = csv.DictReader(csv_data)
    parts = []
    for row in reader:
        # filter some weird elements that are deprecated
        if not row['Class ID'].startswith("http://edamontology.org/"):
            continue
        identifier = row['Class ID'].replace("http://edamontology.org/", "")
        part = identifier.split("_")[0]
        if part not in parts:
            edam_dict[part] = {}
            parts.append(part)
        name = row['Preferred Label']
        synonyms = row['Synonyms'].split("|")
        if len(synonyms) == 1 and synonyms[0] == "":
            synonyms = []
        definitions = row['Definitions'].replace("|", "\n")
        parents = row['Parents'].split("|")
        if row['Obsolete'] == "TRUE":
            obsolete = True
        else:
            obsolete = False
        edam_dict[part][identifier] = {
            "name": name,
            "url": row['Class ID'],
            "definition": definitions,
            "synonyms": synonyms,
            "obsolete": bool(obsolete),
            "parents": parents
        }
    with open("./Data/edam.json", "w") as out_file:
        out_file.write(json.dumps(edam_dict, indent=4))
    print("Done")