import json
import math
from threading import Thread

import requests

import settings
from DataBase.DataAccess import BioToolsConnector

base_url = "https://bio.tools/api/t"

class BiotoolsThread(Thread):
    def __init__(self, index):
        Thread.__init__(self)
        self.page_index = index
        self.tools = None
        self.tools_loaded = 0

    def run(self):
        self.tools, self.tools_loaded, _ = get_page(self.page_index)


def get_page(index):
    url = f"https://bio.tools/api/t/?page={index}&format=json&sort=name&ord=asc"
    response = requests.get(url)
    parsed_response = json.loads(response.content)
    tools_loaded = len(parsed_response['list'])
    tools_total = parsed_response['count']
    return parsed_response['list'], tools_loaded, tools_total


def load():
    max_threads = int(settings.max_parallel_requests)
    print("Retrieving biotools definition...", end="\r")

    first_tools, tools_loaded, total_tools = get_page(1)

    requests_to_make = math.ceil(total_tools / tools_loaded)
    requests_made = 0
    loaded = 0
    full_cycles_to_make = math.floor(requests_to_make / max_threads)
    full_cycles_made = 0

    requests_left_to_make = requests_to_make - (full_cycles_to_make * max_threads)

    while full_cycles_made < full_cycles_to_make:
        threads = [None] * max_threads
        for i in range(0, max_threads):
            threads[i] = BiotoolsThread(requests_made + 1)
            threads[i].start()
            requests_made += 1
        for i in range(0, max_threads):
            threads[i].join()
            BioToolsConnector.insert_biotools(threads[i].tools)
            loaded += threads[i].tools_loaded
        print(f"Retrieving biotools definition... ({loaded}/{total_tools})", end="\r")
        full_cycles_made += 1

    threads = [None] * requests_left_to_make
    for j in range(0, requests_left_to_make):
        threads[j] = BiotoolsThread(requests_made + 1)
        threads[j].start()
        requests_made += 1
    for j in range(0, requests_left_to_make):
        threads[j].join()
        BioToolsConnector.insert_biotools(threads[j].tools)
        loaded += threads[j].tools_loaded
        print(f"Retrieving biotools definition... ({loaded}/{total_tools})", end="\r")

    print("Retrieving biotools definition... Done                                                            ")
