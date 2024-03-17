"""
This script analyzes the distribution of tools across operations. This will produce an overview of the most common operations.
"""
import datetime
import matplotlib.pyplot as plt
from collections import OrderedDict
from textwrap import wrap
import settings
import EDAMUtil

db = settings.db_connection.connection

start = datetime.datetime.now()

operations_list = db.execute(f"""SELECT Child_EDAM_id FROM EDAM_operations_structure WHERE Parent_EDAM_id = 'operation_0004'""").fetchall()
names = []
counts = []
ops = []
for top_level_op in operations_list:
    tlop_id = top_level_op[0]
    op_data = db.execute(f"SELECT Name FROM EDAM WHERE EDAM_id='{tlop_id}'")
    op_name = op_data.fetchone()[0]
    tools = []
    tools_tlop = db.execute(f"""SELECT Biotools_id FROM biotools_tools_operations WHERE EDAM_id = '{tlop_id}'""").fetchall()
    for tool in tools_tlop:
        tools.append(tool[0])

    sub_ops = EDAMUtil.get_all_suboperations(tlop_id)
    for sub_op in sub_ops:
        tools_subop = db.execute(f"""SELECT Biotools_id FROM biotools_tools_operations WHERE EDAM_id = '{sub_op}'""")
        for tool in tools_subop:
            tools.append(tool[0])
    ops.append((op_name, len(set(tools))))

for key in sorted(ops, key=lambda x: x[1]):
    names.append(key[0])
    counts.append(key[1])

plt.figure(1)
#plt.title("Distributions of Tools across Operation Categories")
plt.xlabel("Number of Tools with Operation")
plt.ylabel("Operation")
plt.barh(names, counts)
plt.tight_layout()
plt.savefig('D:\\Priv\\repository\\toolfinder\\Data\\images\\distribution_of_tools_across_operation_categories.png')
plt.show()
