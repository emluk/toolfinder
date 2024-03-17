import datetime

import EDAMUtil
import settings

db = settings.db_connection.connection

protein_sequence_ops = EDAMUtil.get_all_suboperations('operation_2479')

sequence_alignment_ops = EDAMUtil.get_all_suboperations('operation_0292')

protein_tools = []
for op in protein_sequence_ops:
    tools = db.execute(f"""SELECT Biotools_id FROM biotools_tools_operations WHERE EDAM_id = '{op}'""").fetchall()
    protein_tools += tools

protein_tools = set(protein_tools)

sequence_tools = []
for op in sequence_alignment_ops:
    tools = db.execute(f"SELECT Biotools_id FROM biotools_tools_operations WHERE EDAM_id = '{op}'").fetchall()
    sequence_tools += tools

sequence_tools = set(sequence_tools)

sequence_tools_counter = 0
protein_tools_counter = 0

sequence_tools_formats = {}
protein_tools_formats = {}

for tool in sequence_tools:
    tool_id = tool[0]
    raw_data = db.execute(f"""SELECT LastUpdate From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()
    last_updated = raw_data[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year < 2021:
        continue
    sequence_tools_counter += 1
    raw_input_data = db.execute(f"""SELECT * FROM biotools_tools_inputs where Biotools_id='{tool_id}'""").fetchall()
    for _, data_id, format_id in raw_input_data:
        format_name = db.execute(f"SELECT Name FROM EDAM where EDAM_id='{format_id}'").fetchone()[0]
        if format_name not in sequence_tools_formats:
            sequence_tools_formats[format_name] = 1
        else:
            sequence_tools_formats[format_name] += 1

print(sequence_tools_formats)

for tool in protein_tools:
    tool_id = tool[0]
    raw_data = db.execute(f"""SELECT LastUpdate From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()
    last_updated = raw_data[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year < 2021:
        continue
    protein_tools_counter += 1
    raw_input_data = db.execute(f"""SELECT * FROM biotools_tools_inputs where Biotools_id='{tool_id}'""").fetchall()
    for _, data_id, format_id in raw_input_data:
        format_name = db.execute(f"SELECT Name FROM EDAM where EDAM_id='{format_id}'").fetchone()[0]
        if format_name not in protein_tools_formats:
            protein_tools_formats[format_name] = 1
        else:
            protein_tools_formats[format_name] += 1
print(protein_tools_formats)