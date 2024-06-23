import os
import spacy
import settings
import nltk
nltk.data.path = [settings.config['nltk']['path']]
nlp = spacy.load('en_core_web_sm')

if os.path.isfile(settings.config["nltk"]["path"]+r"\tokenizers\punkt.zip"):
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
        nltk.download('popular', download_dir=settings.config["nltk"]["path"])
        nltk.download('stopwords', download_dir=settings.config["nltk"]["path"])
else:
    nltk.download('punkt')
    nltk.download('popular', download_dir=settings.config["nltk"]["path"])
    nltk.download('stopwords', download_dir=settings.config["nltk"]["path"])

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))
class KeywordSearch:
    @staticmethod
    def evaluate(description, keyword_list, dummy_parameter):
        for keyword in keyword_list:
            if keyword.lower() in description.lower():
                return True
        return False


class WordDistance:
    @staticmethod
    def evaluate(description, dictionary, max_distance):
        description = description.lower()
        description_tokenized = word_tokenize(description)
        description_filtered = []
        for word in description_tokenized:
            if word not in stop_words:
                description_filtered.append(word)
        for keyword in dictionary.keys():
            kw_occurences = []
            ow_occurences = []
            keyword=keyword.lower()
            for i, word in enumerate(description_filtered):
                if word == keyword:
                    kw_occurences.append(i)
                    continue
                for other_word in dictionary[keyword]:
                    if word == other_word:
                        ow_occurences.append(i)
                for kw_index in kw_occurences:
                    for ow_index in ow_occurences:
                        if (kw_index < ow_index and ow_index - kw_index <= max_distance + 1) or (kw_index > ow_index and kw_index - ow_index <= max_distance + 1):
                            return True
        return False


class DependencyParsing:
    @staticmethod
    def evaluate(description, dictionary, dummy_parameter):
        document = nlp(description)
        for token in document:
            if token.text.lower() in dictionary.keys():
                for word in token.subtree:
                    if word.text.lower() in dictionary[token.text.lower()]:
                        return True
                for word in token.ancestors:
                    if word.text.lower() in dictionary[token.text.lower()]:
                        return True
        return False


# print(WordDistance.evaluate("This tool uses parallel processing", {'parallel': ['processing']}, 5))
# print(DependencyParsing.evaluate("This tool uses parallel processing", {'parallel': ['processing']}))
# print(KeywordSearch.evaluate("This tool uses parallel processing",  ['processing', 'parallel']))