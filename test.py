# import json
# import os.path
#
# import settings
# import nltk
# nltk.data.path = [settings.config["nltk"]["path"]]
#
# #if os.path.isfile(settings.config["nltk"]["path"]+r"\tokenizers\punkt.zip"):
#
# print()
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     nltk.download('popular', download_dir=settings.config["nltk"]["path"])
#     nltk.download('stopwords', download_dir=settings.config["nltk"]["path"])
#
# from nltk.corpus import stopwords, wordnet
# from nltk.tokenize import sent_tokenize, word_tokenize
# from nltk.stem import SnowballStemmer, WordNetLemmatizer
#
#
#
# def process(sentence):
#     # tokenize
#     sentence_tokenized = word_tokenize(sentence)
#     # remove stop words
#     stop_words = set(stopwords.words('english'))
#     filtered = []
#     for word in sentence_tokenized:
#         if word not in stop_words:
#             filtered.append(word)
#
#     stemmed = []
#     stemmer = SnowballStemmer(language='english')
#     for word in filtered:
#         stemmed.append(stemmer.stem(word))
#
#     pos_unusable = nltk.pos_tag(stemmed)
#     pos_list = []
#     for word, tag in pos_unusable:
#         if len(word) == 1:
#             continue # filter punctuation
#         if tag.startswith("J"):
#             pos = wordnet.ADJ
#         elif tag.startswith("V"):
#             pos = wordnet.VERB
#         elif tag.startswith("N"):
#             pos = wordnet.NOUN
#         elif tag.startswith("R"):
#             pos = wordnet.ADV
#         else:
#             pos = wordnet.NOUN
#
#         pos_list.append((word, pos))
#
#     lemmatized = []
#     lemmatizer = WordNetLemmatizer()
#
#     for word, pos in pos_list:
#         lemmatized.append(lemmatizer.lemmatize(word, pos=pos))
#     return list(set(lemmatized))
#
# biotools_description = ("Collection of protein interactions for which high-resolution three-dimensional structures are known. The "
#            "interface residues are presented for each interaction type individually, plus global domain interfaces at "
#            "which one or more partners (domains or peptides) bind. The web server visualizes these interfaces along "
#            "with atomic details of individual interactions using Jmol.")
#
# operations = {
#     "operation_0246": {"Description": "Identify structural domains in a protein structure from first principles (for example calculations on structural compactness)."},
#     "operation_0248": {"Description": "Calculate or extract inter-atomic, inter-residue or residue-atom contacts, distances and interactions in protein structure(s)."},
#     "operation_0303": {"Description": "Recognize (predict and identify) known protein structural domains or folds in protein sequence(s) which (typically) are not accompanied by any significant sequence similarity to know structures.\nMethods use some type of mapping between sequence and fold, for example secondary structure prediction and alignment, profile comparison, sequence properties, homologous sequence search, kernel machines etc. Domains and folds might be taken from SCOP or CATH."},
#     "operation_2492": {"Description": "Predict the interactions of proteins with other proteins."},
#     "operation_2949": {"Description": "Analyse the interactions of proteins with other proteins."}
# }
# operation_edam_id = "operation_2949"
# operation_description = "Analyse the interactions of proteins with other proteins."
#
# source = process(biotools_description)
# for key in list(operations.keys()):
#     operations[key]['processed'] = process(operations[key]["Description"])
#     present_counter = 0
#     matches = []
#     for word in source:
#         if word in operations[key]['processed']:
#             matches.append(word)
#             present_counter += 1
#     operations[key]['probability'] = (present_counter / len(operations[key]["processed"])) * 100
#     operations[key]['matches'] = matches
#     break
# print(source)
# print(json.dumps(operations, indent=4))
#

import settings

x = settings.db_connection.connection.execute(f"Select Biotools_id from biotools_tools_info where instr(Description, 'Protein') and instr(Description, 'Interaction')")
for item in x.fetchall():
    print(item)