import datetime
import json

import matplotlib.pyplot as plt
from collections import OrderedDict
from textwrap import wrap
import settings

db = settings.db_connection.connection

sequence_analysis_operations = db.execute(f"SELECT EDAM_id, Name FROM EDAM WHERE instr(Parents, 'operation_2403')")


op_data = []
for op in sequence_analysis_operations:
    op_id = op[0]
    op_name = op[1]

    raw_count = db.execute(f" SELECT COUNT(*) FROM biotools_tools_operations WHERE EDAM_id='{op_id}'")
    op_count = raw_count.fetchone()[0]
    op_data.append((op_name, op_count))

sorted_op_data = sorted(op_data, key=lambda x: x[1], reverse=True)
names = []
counts = []
for y in sorted_op_data:
    names.append(y[0])
    counts.append(y[1])


plt.figure(1, figsize=(15, 10))
plt.title("Distribution of Tools across Operations in Sequence Analysis")
plt.barh(names, counts)
plt.tight_layout()
plt.savefig('D:\\Priv\\repository\\toolfinder\\Data\\images\\distribution_of_tools_across_operations_child_of_sequence_analysis.svg')
plt.show()