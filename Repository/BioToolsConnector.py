import json
import requests

base_url = "https://bio.tools/api/t"


def load():
    print("Retrieving biotools definition...", end="\r")

    biotools_dict = {"count": 0, "tools": {}}
    next_page = "?page=1"
    total_tools = 1
    tools_loaded = 0
    while total_tools > tools_loaded and next_page is not None:
        url = f"https://bio.tools/api/t/{next_page}&format=json&sort=name&ord=asc"
        response = requests.get(url)
        parsed_response = json.loads(response.content)
        total_tools = parsed_response['count']
        tools_loaded += len(parsed_response['list'])
        next_page = parsed_response['next']

        for entry in parsed_response['list']:
            identifier = entry["biotoolsID"]
            biotools_dict["tools"][identifier] = entry

        if tools_loaded % 100 == 0:
            print(f"Retrieving biotools definition... ({tools_loaded}/{total_tools})", end="\r")
    biotools_dict["total"] = tools_loaded
    with open("./Data/biotools.json", "w") as out_file:
        out_file.write(json.dumps(biotools_dict, indent=4))
    print("Retrieving biotools definition... Done                                                            ")

