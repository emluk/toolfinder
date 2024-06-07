import settings

db = settings.db_connection.connection


def is_descendant_of(operation_parent, operation_child):
    if operation_parent == 'operation_0004':
        return True
    if operation_parent == operation_child:
        return True
    if is_child_of(operation_parent, operation_child):
        return True
    children = db.execute(f"SELECT Child_EDAM_id FROM EDAM_operations_structure WHERE Parent_EDAM_id = '{operation_parent}'").fetchall()
    for c in children:
        if is_descendant_of(c[0], operation_child):
            return True
    return False


def is_child_of(operation_parent, operation_child):
    children = db.execute(f"SELECT Child_EDAM_id FROM EDAM_operations_structure WHERE Parent_EDAM_id = '{operation_parent}'").fetchall()
    for c in children:
        child = c[0]
        if child == operation_child:
            return True
    return False


def get_children(operation_parent):
    c = db.execute(f"SELECT Child_EDAM_id FROM EDAM_operations_structure WHERE Parent_EDAM_id = '{operation_parent}'").fetchall()
    children = []
    for child in c:
        if child[0] != '':
            children.append(child[0])
    return children


def get_descendants(operation_parent):
    children = get_children(operation_parent)
    for child in children:
        x = get_descendants(child)
        for c in x:
            if c not in children:
                children.append(c)
    return children

