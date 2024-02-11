import json
content = None
with open("./Data/biotools_stats.json", "r") as in_file:
    content = in_file.read()

parsed = json.loads(content)
docs_count = 0
min = 0.0
max = 999999999.99

# boxplot wordcount
# boxplot wordcount processed
# boxplot ratio
# documentation count

word_counts = []
word_counts_processed = []
ratios = []

for entry in parsed:
    if entry['has_documentation']:
        docs_count += 1
    word_counts.append(entry['description']['word_count'])
    word_counts_processed.append(entry['description']['processed_word_count'])
    for op in entry['operations']:
        ratios.append(op['ratio'])
print(f"Documentation: {docs_count}")

lowest_word_count = sorted(word_counts)[0]
highest_word_count = sorted(word_counts)[-1]
average_word_count = sum(word_counts) / len(word_counts)

lowest_processed_word_count = sorted(word_counts_processed)[0]
highest_processed_word_count = sorted(word_counts_processed)[-1]
average_processed_word_count = sum(word_counts_processed) / len(word_counts)

print(f"WC - min: {lowest_word_count}, avg: {average_word_count}, max: {highest_word_count}")
print(f"PWC- min: {lowest_processed_word_count}, avg: {average_processed_word_count}, max: {highest_processed_word_count}")


sorted_ratios = sorted(ratios)
lowest_ratio = sorted_ratios[0]
highest_ratio = sorted_ratios[-1]
avg_ratio = sum(sorted_ratios) / len(sorted_ratios)

print(f"R- min: {lowest_ratio}, avg: {avg_ratio}, max: {highest_ratio}")

