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


def filter_by_output(tool_ids, outputs):
    results = []
    data_and_formats = []
    for i in outputs:
        if ':' in i:
            parts = i.split(':')
            if len(parts) != 2:
                print(f"Invalid output: {i}. Expected format 'data:format'")
                sys.exit(1)
            try:
                data_id, data_name = db.execute(f"SELECT EDAM_id, Name FROM EDAM WHERE EDam_id = '{parts[0]}' OR Name = '{parts[0]}'").fetchone()
                format_id, format_name = db.execute(f"SELECT EDAM_id, Name FROM EDAM WHERE EDam_id = '{parts[1]}' OR Name = '{parts[1]}'").fetchone()
                if not 'data' in data_id or not 'format' in format_id:
                    print(f"Invalid output: {i}. Expected format 'data:format'")
                data_and_formats.append({'data': data_id, 'format': format_id})
            except TypeError:
                print(f"Data '{parts[0]}' or Format '{parts[1]}' not found in EDAM")
        else:
            try:
                eid, name = db.execute(f"SELECT EDAM_id, Name FROM EDAM WHERE Edam_id = '{i}' OR Name = '{i}'").fetchone()
                if 'data' in eid:
                    data_and_formats.append({'data': eid, 'format': None})
                elif 'format' in eid:
                    data_and_formats.append({'data': None, 'format': eid})
                else:
                    print(f"Invalid output: {i}. Expected data or format.")
            except TypeError:
                print(f"Data '{i}' not found in EDAM")
    for tool in tool_ids:
        for item in data_and_formats:
            if item['data'] is not None and item['format'] is not None:
                row = db.execute(f"SELECT * FROM biotools_tools_outputs WHERE Biotools_id='{tool}' AND EDAM_id_data='{item['data']}' AND EDAM_id_format = '{item['format']}'").fetchone()
            elif item['data'] is not None and item['format'] is None:
                row = db.execute(f"SELECT * FROM biotools_tools_outputs WHERE Biotools_id='{tool}' AND EDAM_id_data='{item['data']}'").fetchone()
            elif item['data'] is None and item['format'] is not None:
                row = db.execute(f"SELECT * FROM biotools_tools_outputs WHERE Biotools_id='{tool}' AND EDAM_id_format = '{item['format']}'").fetchone()
            if row is not None:
                if tool not in results:
                    results.append(tool)
    return results


def filter_by_input(tool_ids, inputs):
    results = []
    data_and_formats = []
    for i in inputs:
        if ':' in i:
            parts = i.split(':')
            if len(parts) != 2:
                print(f"Invalid input: {i}. Expected format 'data:format'")
                sys.exit(1)
            try:
                data_id, data_name = db.execute(f"SELECT EDAM_id, Name FROM EDAM WHERE EDam_id = '{parts[0]}' OR Name = '{parts[0]}'").fetchone()
                format_id, format_name = db.execute(f"SELECT EDAM_id, Name FROM EDAM WHERE EDam_id = '{parts[1]}' OR Name = '{parts[1]}'").fetchone()
                if not 'data' in data_id or not 'format' in format_id:
                    print(f"Invalid input: {i}. Expected format 'data:format'")
                data_and_formats.append({'data': data_id, 'format': format_id})
            except TypeError:
                print(f"Data '{parts[0]}' or Format '{parts[1]}' not found in EDAM")
        else:
            try:
                eid, name = db.execute(f"SELECT EDAM_id, Name FROM EDAM WHERE Edam_id = '{i}' OR Name = '{i}'").fetchone()
                if 'data' in eid:
                    data_and_formats.append({'data': eid, 'format': None})
                elif 'format' in eid:
                    data_and_formats.append({'data': None, 'format': eid})
                else:
                    print(f"Invalid input: {i}. Expected data or format.")
            except TypeError:
                print(f"Data '{i}' not found in EDAM")
    for tool in tool_ids:
        for item in data_and_formats:
            if item['data'] is not None and item['format'] is not None:
                row = db.execute(f"SELECT * FROM biotools_tools_inputs WHERE Biotools_id='{tool}' AND EDAM_id_data='{item['data']}' AND EDAM_id_format = '{item['format']}'").fetchone()
            elif item['data'] is not None and item['format'] is None:
                row = db.execute(f"SELECT * FROM biotools_tools_inputs WHERE Biotools_id='{tool}' AND EDAM_id_data='{item['data']}'").fetchone()
            elif item['data'] is None and item['format'] is not None:
                row = db.execute(f"SELECT * FROM biotools_tools_inputs WHERE Biotools_id='{tool}' AND EDAM_id_format = '{item['format']}'").fetchone()
            if row is not None:
                if tool not in results:
                    results.append(tool)
                    break
    return results


def filter_by_label(tool_ids, labels):
    results = []
    for tool in tool_ids:
        for label in labels:
            label = label.strip()
            row = db.execute(f"SELECT * FROM biotools_tools_labels WHERE Biotools_id='{tool}' AND Label='{label}'").fetchone()
            if row is not None:
                results.append(tool)
                break
    return results


def search_tools(operations, keywords, inputs, outputs, labels):
    tool_ids = []
    all_tools = db.execute(f"SELECT Biotools_id FROM biotools_tools_info").fetchall()
    for t in all_tools:
        tool_ids.append(t[0])
    if len(operations) > 0:
        tool_ids = filter_by_operation(tool_ids, operations)
    if len(keywords) > 0:
        tool_ids = filter_by_word_in_description(tool_ids, keywords)
    if len(inputs) > 0:
        tool_ids = filter_by_input(tool_ids, inputs)
    if len(outputs) > 0:
        tool_ids = filter_by_output(tool_ids, outputs)
    if len(labels) > 0:
        tool_ids = filter_by_label(tool_ids, labels)
    return tool_ids


def find_compatible_predecessors(tool, operations, labels):
    try:
        tool_id, tool_name = db.execute(f"SELECT Biotools_id, Name FROM biotools_tools_info WHERE Biotools_id = '{tool}' OR Name = '{tool}'").fetchone()
        input_rows = db.execute(f"SELECT * FROM biotools_tools_inputs WHERE Biotools_id = '{tool_id}'").fetchall()
        if len(input_rows) == 0:
            print(f"Found no documented inputs for '{tool_id}' (Name: '{tool_name}'). Can't find predecessors without inputs.")
            sys.exit(1)
        expected_outputs = []
        for input_row in input_rows:
            expected_outputs.append(f"{input_row[1]}:{input_row[2]}")
        return search_tools(operations, [], [], expected_outputs, labels)
    except TypeError:
        print(f"Tool '{tool}' not found in biotools")


def find_compatible_successors(tool, operations, labels):
    try:
        tool_id, tool_name = db.execute(
            f"SELECT Biotools_id, Name FROM biotools_tools_info WHERE Biotools_id = '{tool}' OR Name = '{tool}'").fetchone()
        output_rows = db.execute(f"SELECT * FROM biotools_tools_outputs WHERE Biotools_id = '{tool_id}'").fetchall()
        if len(output_rows) == 0:
            print(
                f"Found no documented inputs for '{tool_id}' (Name: '{tool_name}'). Can't find predecessors without outputs.")
            sys.exit(1)
        expected_inputs = []
        for output_row in output_rows:
            expected_inputs.append(f"{output_row[1]}:{output_row[2]}")
        return search_tools(operations, [], expected_inputs, [], labels)
    except TypeError:
        print(f"Tool '{tool}' not found in biotools")


def find_replacement(tool, labels):
    try:
        tool_id, tool_name = db.execute(
            f"SELECT Biotools_id, Name FROM biotools_tools_info WHERE Biotools_id = '{tool}' OR Name = '{tool}'").fetchone()

        # find operations of the tool
        operations = db.execute(f"SELECT * FROM biotools_tools_operations WHERE Biotools_id = '{tool_id}'").fetchall()
        if len(operations) == 0:
            print(f"Found no documented operations '{tool_id}' (Name: '{tool_name}'). Can't find replacements.")
        expected_operations = []
        for operation in operations:
            expected_operations.append(operation[1])
        # find inputs of the tool
        input_rows = db.execute(f"SELECT * FROM biotools_tools_inputs WHERE Biotools_id = '{tool_id}'").fetchall()
        if len(input_rows) == 0:
            print(
                f"Found no documented inputs for '{tool_id}' (Name: '{tool_name}'). Can't find replacements without inputs.")
            sys.exit(1)
        expected_inputs = []
        for input_row in input_rows:
            expected_inputs.append(f"{input_row[1]}:{input_row[2]}")

        # find outputs of the tool
        output_rows = db.execute(f"SELECT * FROM biotools_tools_outputs WHERE Biotools_id = '{tool_id}'").fetchall()
        if len(output_rows) == 0:
            print(
                f"Found no documented inputs for '{tool_id}' (Name: '{tool_name}'). Can't find replacements without outputs.")
            sys.exit(1)
        expected_outputs = []
        for output_row in output_rows:
            expected_outputs.append(f"{output_row[1]}:{output_row[2]}")

        return search_tools(expected_operations, [], expected_inputs, expected_outputs, labels)
    except TypeError:
        print(f"Tool '{tool}' not found in biotools")
