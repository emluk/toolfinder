"""
This script analyzes the distribution of tools across operations. This will produce an overview of the most common operations.
"""
import datetime
import matplotlib.pyplot as plt
from collections import OrderedDict
from textwrap import wrap
import settings

db = settings.db_connection.connection

start = datetime.datetime.now()

operations_list = db.execute("SELECT DISTINCT EDAM_id FROM biotools_tools_operations")

collected_operation_data = {}

for op in operations_list:
    op_id = op[0]
    collected_operation_data[op_id] = {}
    # get the name of the operation
    op_data = db.execute(f"SELECT Name FROM EDAM WHERE EDAM_id='{op_id}'")
    op_name = op_data.fetchone()[0]
    collected_operation_data[op_id]["name"] = op_name
    raw_count = db.execute(f" SELECT COUNT(*) FROM biotools_tools_operations WHERE EDAM_id='{op_id}'")
    op_count = raw_count.fetchone()[0]
    collected_operation_data[op_id]["count"] = op_count

x = OrderedDict(sorted(collected_operation_data.items(), key=lambda t: t[1]["count"], reverse=True))
print(x)
print(len(x.keys()))

names = []
counts = []
count = 0
for key in x.keys():
    if count >= 50:
        break
    names.append(x[key]['name'])
    counts.append(x[key]['count'])
    count += 1

plt.figure(1, figsize=(15, 10))
plt.title("Distributions of Tools across Operations (Top 50)")
plt.xlabel("Number of Tools with Operation")
plt.ylabel("Operation")
plt.barh(names, counts)
plt.tight_layout()
#plt.savefig('D:\\Priv\\repository\\toolfinder\\Data\\images\\distribution_of_tools_across_operations.pdf', format='pdf')
plt.show()

end = datetime.datetime.now()
duration = end - start
print(duration)