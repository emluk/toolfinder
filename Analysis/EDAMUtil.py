import settings

db = settings.db_connection.connection

def get_all_suboperations(operation):
    operations = []
    operations.append(operation)
    ops_raw = db.execute(f"""SELECT * FROM EDAM_operations_structure WHERE Parent_EDAM_id='{operation}'""").fetchall()

    if(len(ops_raw) == 1 and ops_raw[0][1] == ''):
        return [ops_raw[0][0]]

    for op in ops_raw:
        children = get_all_suboperations(op[1])
        operations = operations + children
        operations.append(op[1])
    return list(set(operations))


