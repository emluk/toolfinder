import json
import sys
from datetime import datetime

import settings
import os
import nltk
nltk.data.path = [settings.config["nltk"]["path"]]

if os.path.isfile(settings.config["nltk"]["path"]+r"\tokenizers\punkt.zip"):
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('popular', download_dir=settings.config["nltk"]["path"])
        nltk.download('stopwords', download_dir=settings.config["nltk"]["path"])
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import SnowballStemmer, WordNetLemmatizer


def process(sentence):
    # tokenize
    sentence_tokenized = word_tokenize(sentence)
    # remove stop words
    stop_words = set(stopwords.words('english'))
    filtered = []
    for word in sentence_tokenized:
        if word not in stop_words:
            filtered.append(word)

    stemmed = []
    stemmer = SnowballStemmer(language='english')
    for word in filtered:
        stemmed.append(stemmer.stem(word))

    pos_unusable = nltk.pos_tag(stemmed)
    pos_list = []
    for word, tag in pos_unusable:
        if len(word) == 1:
            continue # filter punctuation
        if tag.startswith("J"):
            pos = wordnet.ADJ
        elif tag.startswith("V"):
            pos = wordnet.VERB
        elif tag.startswith("N"):
            pos = wordnet.NOUN
        elif tag.startswith("R"):
            pos = wordnet.ADV
        else:
            pos = wordnet.NOUN

        pos_list.append((word, pos))

    lemmatized = []
    lemmatizer = WordNetLemmatizer()

    for word, pos in pos_list:
        lemmatized.append(lemmatizer.lemmatize(word, pos=pos))
    return list(set(lemmatized))

def main():
    start_time = datetime.now()

    db = settings.db_connection.connection
    biotools_data = []

    with open("./Data/biotools_stats.json", "w") as outfile:
        all_data = db.execute("SELECT * FROM biotools_tools_info")
        for row in all_data:
            tool_data = {}
            tool_id = row[0]

            tool_data["id"] = tool_id

            raw_description = row[4]
            processed_description = process(raw_description)

            tool_data['has_documentation'] = False
            if row[6] != "None":
                tool_data['has_documentation'] = True
            tool_data["description"] = {}
            tool_data["description"]["word_count"] = len(raw_description.split(" "))
            tool_data["description"]["processed_word_count"] = len(processed_description)
            tool_data["operations"] = []


            raw_operations = db.execute(f"SELECT EDAM_id FROM biotools_tools_operations WHERE instr(Biotools_id, '{tool_id}')")
            for op in raw_operations:
                operation_data = {}
                operation_id = op[0]
                description_row = db.execute(f"SELECT Definition FROM EDAM WHERE instr(EDAM_id, '{operation_id}')")
                raw_description = description_row.fetchone()
                processed_operation_description = process(raw_description[0])
                # keyword matching
                matches = 0
                operation_word_count = len(processed_operation_description)
                for word in processed_operation_description:
                    if word in processed_description:
                        matches += 1
                ratio = matches/operation_word_count
                operation_data['id'] = operation_id
                operation_data['description'] = raw_description[0]
                operation_data['word_count'] = len(raw_description[0].split(" "))
                operation_data['processed_word_count'] = operation_word_count
                operation_data['matches'] = matches
                operation_data['ratio'] = ratio
                tool_data['operations'].append(operation_data)
            biotools_data.append(tool_data)
        outfile.write(json.dumps(biotools_data, indent=4))
    end_time = datetime.now()
    print((end_time - start_time).total_seconds())



    # number of words in description
    # number of words in description without stopwords and after stemming
    # number of operations
    # keyword matching between each operation and the description
    # number of tools that have documentation linked


if __name__ == '__main__':
    main()