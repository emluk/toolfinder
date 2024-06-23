import json

import spacy
from spacy.lang.en import stop_words
from string import punctuation
nlp = spacy.load('en_core_web_sm')


def create(keyword, property, in_file_path, out_file_path):
    data = None
    with open(in_file_path, 'r') as f:
        data = json.load(f)
    stopwords = stop_words.STOP_WORDS
    punct = list(punctuation)
    results = {}
    for key in data.keys():
        description = data[key]['Description']
        prop = data[key][property]
        if prop:
            document = nlp(description)
            for token in document:
                if keyword in token.text:
                    connected_words = list(token.ancestors)
                    connected_words += list(token.children)
                    words_to_add = []
                    for w in connected_words:
                        if w.text in stopwords or w in punct:
                            continue
                        if w.pos_ not in ['NOUN', 'PROPN']:
                            continue
                        if w.text not in words_to_add:
                            words_to_add.append(w.text.lower())
                        if w.lemma_ != w.text:
                            words_to_add.append(w.lemma_)
                    if len(words_to_add) > 0:
                        if token.text not in results.keys():
                            results[token.text] = []
                        results[token.text] += words_to_add
    for key in results.keys():
        results[key] = sorted(list(set(results[key])))

    with open(out_file_path, 'w') as f:
        json.dump(results, f, indent=4)
        print(f"Dictionary written to {out_file_path}")