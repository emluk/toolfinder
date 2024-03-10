import datetime
import json

import matplotlib.pyplot as plt
from collections import OrderedDict
from textwrap import wrap
import settings

db = settings.db_connection.connection

edam_operations = db.execute(
    """SELECT EDAM_id, Parents FROM EDAM WHERE EDAM_category = 'operation' AND Obsolete = 0""").fetchall()

tree = {}
for x in edam_operations:
    edam_id = x[0]
    edam_parents_unfiltered = x[1].replace('[', '').replace(']', '').replace("'", '').split(',')
    edam_parents = []
    for parent in edam_parents_unfiltered:
        if 'http://edamontology.org/operation' in parent:
            parent_name = parent.replace('http://edamontology.org/', '').replace(' ', '')
            edam_parents.append(parent_name.replace(' ', ''))
            if parent_name not in tree.keys():
                tree[parent_name] = []
            tree[parent_name].append(edam_id.replace(' ', ''))

    if edam_id not in tree.keys():
        tree[edam_id.replace(' ', '')] = []



db.execute('''create table if not exists EDAM_operations_structure 
(
    Parent_EDAM_id TEXT not null,
    Child_EDAM_id  TEXT,
    constraint EDAM_operations_structure_pk
        primary key (Parent_EDAM_id, Child_EDAM_id)
);
''')
db.commit()
print(len(tree.keys()))
for x in tree.keys():
    if len(tree[x]) == 0:
        db.execute(f"""insert into EDAM_operations_structure (Parent_EDAM_id, Child_EDAM_id) 
                        values("{x}", "")
                        on conflict do nothing;""")
        continue
    for child in tree[x]:
        db.execute(f"""insert into EDAM_operations_structure (Parent_EDAM_id, Child_EDAM_id) 
                        values("{x}", "{child}")
                        on conflict do nothing;""")
        db.commit()