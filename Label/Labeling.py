import json

import NLP.NER.NER
from DataBase.DataAccess import BioToolsConnector
from settings import db_connection

db = db_connection.connection

def assign(tools, label):
    label = label.strip()
    for tool in tools:
        tool_details = db.execute(f"SELECT Biotools_Id, Name FROM biotools_tools_info WHERE Biotools_id = '{tool}' OR Name = '{tool}'").fetchone()
        if tool_details is not None:
            tool_name = tool_details[1]
            tool_id = tool_details[0]
            print(f"Assigning label '{label}' to tool {tool_id}")
            BioToolsConnector.insert_label(tool_id, label)
        else:
            print(f"Could not find any tool with name or id '{tool}'")

def remove(tools, label):
    label = label.strip()
    for tool in tools:
        tool_details = db.execute(
            f"SELECT Biotools_Id, Name FROM biotools_tools_info WHERE Biotools_id = '{tool}' OR Name = '{tool}'").fetchone()
        if tool_details is not None:
            tool_name = tool_details[1]
            tool_id = tool_details[0]
            print(f"Removing label '{label}' to tool {tool_id}")
            BioToolsConnector.remove_label(tool_id, label)
        else:
            print(f"Could not find any tool with name or id '{tool}'")

def clear_all():
    db.execute("DELETE FROM biotools_tools_labels")
    db.commit()


def label_all(algorithm, dictionary_path, label, max_distance = None):
    with open(dictionary_path, 'r') as dict_file:
        dictionary = json.load(dict_file)
        label = label.strip()
        if algorithm == 'KeywordSearch':
            dictionary = list(dictionary.keys())
            evaluate = NLP.NER.NER.KeywordSearch.evaluate
        elif algorithm == 'WordDistance':
            evaluate = NLP.NER.NER.WordDistance.evaluate
        elif algorithm == 'DependencyParsing':
            evaluate = NLP.NER.NER.DependencyParsing.evaluate
        biotools_data = db.execute(f"SELECT Biotools_Id, Description FROM biotools_tools_info").fetchall()
        labeled_tools = []
        for tool in biotools_data:
            id = tool[0]
            description = tool[1]
            if evaluate(description, dictionary, max_distance):
                BioToolsConnector.insert_label(id, label)
                labeled_tools.append(id)
        print(f"Labeled {len(labeled_tools)} tools")
        print(labeled_tools)



