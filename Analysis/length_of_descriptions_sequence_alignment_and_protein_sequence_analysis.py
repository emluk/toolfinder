import datetime
import matplotlib.pyplot as plt
import settings
import numpy as np
import EDAMUtil
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

# protein_years_updated = {}
sequence_description_counts = {}
protein_description_counts = {}
step = 10
for i in range(0,150, step):
    if i == 0:
        sequence_description_counts[f"{i}-{i+step}"] = {
            'min': i,
            'max': i+10,
            'count': 0
        }
        protein_description_counts[f"{i}-{i + step}"] = {
            'min': i,
            'max': i + 10,
            'count': 0
        }
    else:
        sequence_description_counts[f"{i+1}-{i+step}"] = {
            'min': i+1,
            'max': i+10,
            'count': 0
        }
        protein_description_counts[f"{i + 1}-{i + step}"] = {
            'min': i + 1,
            'max': i + 10,
            'count': 0
        }

max_count = 0
for tool in sequence_tools:
    tool_id = tool[0]
    raw_data = db.execute(f"""SELECT LastUpdate, Description From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()
    last_updated = raw_data[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year < 2021:
        continue
    description = raw_data[1]
    word_count = len(description.split(' '))
    if word_count > max_count:
        max_count = word_count
    for r in sequence_description_counts.keys():
        if sequence_description_counts[r]['min'] <= word_count <= sequence_description_counts[r]['max']:
            sequence_description_counts[r]['count'] += 1
print(f"Max sequence count: {max_count}")
max_count = 0
for tool in protein_tools:
    tool_id = tool[0]
    raw_data = db.execute(f"""SELECT LastUpdate, Description From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()
    last_updated = raw_data[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year < 2021:
        continue
    description = raw_data[1]
    word_count = len(description.split(' '))
    if word_count > max_count:
        max_count = word_count
    for r in protein_description_counts.keys():
        if protein_description_counts[r]['min'] <= word_count <= protein_description_counts[r]['max']:
            protein_description_counts[r]['count'] += 1
print(f"Max protein count: {max_count}")
print(sequence_description_counts)
print(protein_description_counts)

ranges = []
sequence_values = []
protein_values = []
for key in sequence_description_counts.keys():
    ranges.append(key)
    sequence_values.append(sequence_description_counts[key]['count'])
    protein_values.append(protein_description_counts[key]['count'])

X_axis = np.arange(len(ranges))

plt.figure(1)

#plt.title("Last Update on Tools in Sequence Alignment and Protein Sequence Analysis")
plt.xlabel("Words in Description")
plt.ylabel("Number of Tools")

plt.bar(X_axis - 0.2, sequence_values, 0.4, label="Sequence Aligment")
plt.bar(X_axis + 0.2, protein_values, 0.4, label="Protein Sequence Analysis")
plt.xticks(X_axis, ranges,rotation=45)
plt.legend()
plt.tight_layout()
plt.savefig('D:\\Priv\\repository\\toolfinder\\Data\\images\\protein_sequence_analysis_and_sequence_alignment_description_length.png', format='png')
plt.show()