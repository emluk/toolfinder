import settings

db = settings.db_connection.connection

tool_ids_raw = db.execute("SELECT Biotools_ID from biotools_tools_info").fetchall()
tool_counters = {
    "inputs": {},
    "outputs": {},
    "operations": {}
}
for tool in tool_ids_raw:
    tool_id = tool[0]
    inputs = db.execute(f"SELECT EDAM_id_data, EDAM_id_format")