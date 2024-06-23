from Utility import DB

from sqlite3 import Error

from settings import db_connection
db = db_connection.connection


def create_edam_table():
    print("Initializing EDAM table...", end=" ")
    try:
        db.execute('''create table EDAM
                                       (
                                           EDAM_id       TEXT not null
                                               constraint EDAM_pk
                                                   primary key,
                                           EDAM_category TEXT,
                                           EDAM_url      TEXT,
                                           Name          TEXT not null,
                                           Definition    TEXT,
                                           Synonyms      TEXT,
                                           Obsolete      TEXT  not null,
                                           Parents       TEXT
                                       );
                                           ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")



def create_edam_operations_structure_table():
    print("Initializing EDAM Operations structure Table...", end=" ")
    try:
        db.execute('''create table if not exists EDAM_operations_structure 
        (
            Parent_EDAM_id TEXT not null,
            Child_EDAM_id  TEXT,
            constraint EDAM_operations_structure_pk
                primary key (Parent_EDAM_id, Child_EDAM_id)
        );
        ''')
    except Error as e:
        print(f"Error: {str(e)}")
        return
    print("Done")


def insert_edam(rows):
    for row in rows:
        obsolete = "FALSE"
        if row["obsolete"]:
            obsolete = "TRUE"
        for key in list(row.keys()):
            if key != "obsolete":
                row[key] = DB.escape_input(str(row[key]))
        db.execute(f'''insert into EDAM (EDAM_id, EDAM_category, EDAM_url, Name, Definition, Synonyms, Obsolete, Parents)
                                    values ("{row["edam_id"]}", "{row["edam_category"]}","{row["edam_url"]}", "{row["name"]}", "{row["definition"]}", "{row["synonyms"]}", {obsolete}, "{row["parents"]}")
                                    on conflict do nothing;
                                ''')
    db.commit()
    # building structure of edam operations table
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