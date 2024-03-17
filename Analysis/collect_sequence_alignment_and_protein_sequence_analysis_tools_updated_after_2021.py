import datetime

import EDAMUtil
import settings

db = settings.db_connection.connection

protein_sequence_ops = EDAMUtil.get_all_suboperations('operation_2479')
print(len(protein_sequence_ops))
sequence_alignment_ops = EDAMUtil.get_all_suboperations('operation_0292')
print(len(sequence_alignment_ops))
protein_tools = []
for op in protein_sequence_ops:
    tools = db.execute(f"""SELECT Biotools_id FROM biotools_tools_operations WHERE EDAM_id = '{op}'""").fetchall()
    protein_tools += tools

protein_tools = set(protein_tools)
print(len(protein_tools))
sequence_tools = []
for op in sequence_alignment_ops:
    tools = db.execute(f"SELECT Biotools_id FROM biotools_tools_operations WHERE EDAM_id = '{op}'").fetchall()
    sequence_tools += tools

sequence_tools = set(sequence_tools)
print(len(sequence_tools))

sequence_tools_updated_after_2021 = []
protein_tools_updated_after_2021 = []

for tool in sequence_tools:
    tool_id = tool[0]
    raw_data = db.execute(f"""SELECT LastUpdate, Description From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()
    last_updated = raw_data[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year < 2021:
        continue
    sequence_tools_updated_after_2021.append(tool_id)

with open("../Data/out/sequence_tools_updated_after_2021.txt", "w") as seq_out_file:
    seq_out_file.write("\n".join(sequence_tools_updated_after_2021))

for tool in protein_tools:
    tool_id = tool[0]
    raw_data = db.execute(f"""SELECT LastUpdate, Description From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()
    last_updated = raw_data[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year < 2021:
        continue
    protein_tools_updated_after_2021.append(tool_id)

with open("../Data/out/protein_tools_updated_after_2021.txt", "w") as seq_out_file:
    seq_out_file.write("\n".join(protein_tools_updated_after_2021))