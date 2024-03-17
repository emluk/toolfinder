import datetime
import json

import matplotlib.pyplot as plt
from collections import OrderedDict
from textwrap import wrap
import settings
import EDAMUtil
db = settings.db_connection.connection

sequence_analysis_operations = EDAMUtil.get_all_suboperations('operation_2403')
op_data = []
for op in sequence_analysis_operations:
    tools = []
    op_name = db.execute(f"SELECT Name from EDAM WHERE EDAM_id = '{op}'").fetchone()[0]
    raw_data = db.execute(f"""SELECT Biotools_id From biotools_tools_operations Where EDAM_id = '{op}'""").fetchall()
    for raw_tool in raw_data:
        tools.append(raw_tool[0])
    op_data.append((op_name, len(set(tools))))

sorted_op_data = sorted(set(op_data), key=lambda o: o[1])
print(len(sorted_op_data))
names = []
counts = []

for x in sorted_op_data[-20:]:
    names.append(x[0])
    counts.append(x[1])

print(counts)
print(names)

plt.figure(1)
#plt.title("Distribution of Tools across Operations \nthat are Children of Sequence Analysis")
plt.xlabel("Number of Tools with Operation")
plt.ylabel("Operation")
plt.barh(names, counts)
plt.tight_layout()
plt.savefig('D:\\Priv\\repository\\toolfinder\\Data\\images\\distribution_of_tools_across_operations_child_of_sequence_analysis.png')
plt.show()