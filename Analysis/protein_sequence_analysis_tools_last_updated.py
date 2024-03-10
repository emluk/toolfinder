import datetime
import matplotlib.pyplot as plt
import settings

db = settings.db_connection.connection

tools_sequence_analysis = db.execute("""SELECT Biotools_id FROM biotools_tools_operations WHERE EDAM_id = 'operation_2479'""").fetchall()

years_updated = {}
for tool in tools_sequence_analysis:
    tool_id = tool[0]
    last_updated = db.execute(f"""SELECT LastUpdate From biotools_tools_info where Biotools_id='{tool_id}'""").fetchone()[0]
    updated_year = datetime.datetime.strptime(last_updated.split('T')[0], "%Y-%m-%d").year
    if updated_year not in years_updated.keys():
        years_updated[updated_year] = 0
    years_updated[updated_year] += 1

print(years_updated)
sorted_years = sorted(years_updated.keys())
sorted_counts = []

for year in sorted_years:
    sorted_counts.append(years_updated[year])

plt.figure(1, figsize=(15, 10))
plt.title("Last Update on Tools in Protein Sequence Analysis (operation_2479)")
plt.bar(sorted_years, sorted_counts)
plt.tight_layout()
plt.savefig('D:\\Priv\\repository\\toolfinder\\Data\\images\\protein_sequence_alignment_last_updated.svg')
plt.show()