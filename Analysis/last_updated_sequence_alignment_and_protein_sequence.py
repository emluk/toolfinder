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
sequence_years_updated = {}
for tool in sequence_tools:
    tool_id = tool[0]
    last_updated = db.execute(f"""SELECT LastUpdate From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year not in sequence_years_updated.keys():
        sequence_years_updated[updated_year] = 0
    sequence_years_updated[updated_year] += 1

protein_years_updated = {}
for tool in protein_tools:
    tool_id = tool[0]
    last_updated = db.execute(f"""SELECT LastUpdate From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year not in protein_years_updated.keys():
        protein_years_updated[updated_year] = 0
    protein_years_updated[updated_year] += 1

sequence_years_sorted = sorted(sequence_years_updated.keys())
sequence_counts = []
protein_counts = []
for year in sequence_years_sorted:
    sequence_counts.append(sequence_years_updated[year])
    protein_counts.append(protein_years_updated[year])

X_axis = np.arange(len(sequence_years_sorted))

plt.figure(1)

#plt.title("Last Update on Tools in Sequence Alignment and Protein Sequence Analysis")
plt.xlabel("Year of Last Update")
plt.ylabel("Number of Tools")

plt.bar(X_axis - 0.2, sequence_counts, 0.4, label="Sequence Aligment")
plt.bar(X_axis + 0.2, protein_counts, 0.4, label="Protein Sequence Analysis")
plt.xticks(X_axis, sequence_years_sorted)
plt.legend()
plt.tight_layout()
plt.savefig('D:\\Priv\\repository\\toolfinder\\Data\\images\\last_updated_protein_sequence_analysis_and_sequence_alignment.png')
plt.show()