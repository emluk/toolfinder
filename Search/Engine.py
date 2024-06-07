import json
import sys

from settings import db_connection
from Utility import EDAM
db = db_connection.connection

def get_operation_info(operation_string):
    op_string = operation_string.strip()
    op_string = op_string.replace('sub(', '').replace(')', '').replace('child(', '').strip()
    if op_string.startswith('operation_'):
        op_name = db.execute(f"SELECT Name FROM EDAM where EDAM_id = '{op_string}'").fetchone()
        if op_name is None:
            print(f"Could not resolve id '{op_string}'")
            sys.exit(1)
        return op_string, op_name[0]
    else:
        op_id = db.execute(f"SELECT EDAM_id FROM EDAM WHERE Name = '{op_string}'").fetchone()
        if op_id is None:
            print(f"Could not find operation with name '{op_string}'")
            sys.exit(1)
        return op_id[0], op_string


def filter_by_operation(tool_ids, operations):
    operation_ids = []
    results = []
    for operation in operations:
        op_id, op_name = get_operation_info(operation)
        operation_ids.append(op_id)
        children = []
        if operation.startswith('sub('):
            children = EDAM.get_descendants(op_id)
            print(len(children))
        elif operation.startswith('child('):
            children = EDAM.get_children(op_id)
        for child in children:
            if child not in operation_ids:
                operation_ids.append(child)
    for t in tool_ids:
        ops = db.execute(f"SELECT EDAM_id FROM biotools_tools_operations WHERE Biotools_id = '{t}'").fetchall()
        for op in ops:
            if op[0] in operation_ids:
                results.append(t)
    return list(set(results))


def filter_by_word_in_description(tool_ids, keywords):
    results = []
    for tool_id in tool_ids:
        description = db.execute(f"SELECT Description FROM biotools_tools_info WHERE Biotools_id = '{tool_id}'").fetchone()[0]
        for keyword in keywords:
            temp_desc = description
            if keyword.islower():
                temp_desc = description.lower()
            if keyword in temp_desc:
                results.append(tool_id)
    return list(set(results))


def search_tools(operations, keywords):
    tool_ids = []
    all_tools = db.execute(f"SELECT Biotools_id FROM biotools_tools_info").fetchall()
    for t in all_tools:
        tool_ids.append(t[0])
    if len(operations) > 0:
        tool_ids = filter_by_operation(tool_ids, operations)
    if len(keywords) > 0:
        tool_ids = filter_by_word_in_description(tool_ids, keywords)
    return tool_ids







#search_tools(['<operation_0004', 'operation_2945'], [])

# print(filter_by_keyword_in_description(['aurocch', 'ps2'], ['Receiver', 'operating', 'protein']))
# print(filter_by_operation)