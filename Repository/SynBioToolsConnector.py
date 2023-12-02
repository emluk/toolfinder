import json
import requests

base_url = "https://synbiotools.computbiol.com/fastapi/synbiotools?params="


def load():
    print("Retrieving biotools definition...", end="\r")
