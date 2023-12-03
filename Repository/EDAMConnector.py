import csv
from io import StringIO

import settings
import requests

base_url = "https://edamontology.org"


def load():
    print("Retrieving EDAM ontology definition...", end=" ")
    response = requests.get(f"{base_url}/EDAM.csv")
    if response.status_code != 200:
        print(f'Failed to get EDAM definition from {base_url}/EDAM.csv')
        return
    edam_rows = []
    csv_data = StringIO(response.content.decode('utf-8').replace("\r\n", "\n"))
    reader = csv.DictReader(csv_data)
    for row in reader:
        identifier = row['Class ID'].replace("http://edamontology.org/", "")
        part = identifier.split("_")[0]
        name = row['Preferred Label']
        synonyms = row['Synonyms'].split("|")
        if len(synonyms) == 1 and synonyms[0] == "":
            synonyms = []
        definitions = row['Definitions'].replace("|", "\\n")
        parents = row['Parents'].split("|")
        if row['Obsolete'] == "TRUE":
            obsolete = True
        else:
            obsolete = False
        edam_rows.append({
            "edam_id": identifier,
            "edam_category": part,
            "name": name,
            "edam_url": row['Class ID'],
            "definition": definitions,
            "synonyms": synonyms,
            "obsolete": obsolete,
            "parents": parents
        })
    settings.db_connection.insert_edam(edam_rows)
    print("Done")
