import json

import NLP.NER.NER

def to_percentage(number):
    return f"{round(number*100,2)}"

def get_result(manual, automated):
    if manual and automated:
        return 'TP'
    if not manual and automated:
        return 'FP'
    if not manual and not automated:
        return 'TN'
    if manual and not automated:
        return 'FN'

def get_precision(tp, fp):
    if tp == 0: return 0
    return tp / (tp + fp)

def get_recall(tp, fn):
    if tp == 0: return 0
    return tp / (tp + fn)

def get_accuracy(tp, tn, total):
    if total == 0: return 0
    return (tp + tn) / total

def evaluate(test_set_path, property, dictionary_path, algorithm, max_distance = 0):
    test_set = None
    with open(test_set_path, 'r', encoding='utf-8') as f:
        test_set = json.load(f)
    dictionary = None
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        dictionary = json.load(f)
    results = {
        'TP': 0,
        'FP': 0,
        'FN': 0,
        'TN': 0,
        'Accuracy': 0.0,
        'Precision': 0.0,
        'Recall': 0.0,
        'FalsePositive': [],
        'FalseNegative': []
    }
    match algorithm:
        case 'KeywordSearch':
            wordlist = list(dictionary.keys())
            for key in test_set.keys():
                description = test_set[key]['Description']
                manual_result = test_set[key][property]
                automated_result = NLP.NER.NER.KeywordSearch.evaluate(description, wordlist)
                res = get_result(manual_result, automated_result)
                results[res] += 1
                if res == 'FP':
                    results['FalsePositive'].append({'id': key, 'description': description})
                if res == 'FN':
                    results['FalseNegative'].append({'id': key, 'description': description})
        case 'WordDistance':
            for key in test_set.keys():
                description = test_set[key]['Description']
                manual_result = test_set[key][property]
                automated_result = NLP.NER.NER.WordDistance.evaluate(description, dictionary, max_distance)
                res = get_result(manual_result, automated_result)
                results[res] += 1
                if res == 'FP':
                    results['FalsePositive'].append({'id': key, 'description': description})
                if res == 'FN':
                    results['FalseNegative'].append({'id': key, 'description': description})
        case 'DependencyParsing':
            for key in test_set.keys():
                description = test_set[key]['Description']
                manual_result = test_set[key][property]
                automated_result = NLP.NER.NER.DependencyParsing.evaluate(description, dictionary)
                res = get_result(manual_result, automated_result)
                results[res] += 1
                if res == 'FP':
                    results['FalsePositive'].append({'id': key, 'description': description})
                if res == 'FN':
                    results['FalseNegative'].append({'id': key, 'description': description})
        case _:
            print("Invalid algorithm. Pick 'KeywordSearch' or 'WordDistance' or 'DependencyParsing'")
    total = results['TP'] + results['FP'] + results['FN'] + results['TN']
    results['Accuracy'] = get_accuracy(results['TP'], results['TN'], total)
    results['Precision'] = get_precision(results['TP'], results['FP'])
    results['Recall'] = get_recall(results['TP'], results['FN'])
    return results

results = {}
for p in ['parallel', 'GPU', 'distributed']:
    results[p] = {
        'KeywordSearch': None,
        'WordDistance': None,
        'DependencyParsing': None,
    }
    ts_path = f"D:\\Priv\\repository\\BA-Code\\Data\\Datasets\\Test\\{p}-test-set.json"
    d_path = f"D:\\Priv\\repository\\BA-Code\\Data\\Dictionaries\\{p}-dict.json"
    kw_search_result = evaluate(ts_path, p, d_path, 'KeywordSearch')
    results[p]['KeywordSearch'] = kw_search_result
    #print(f"{p}: KeywordSearch {kw_search_result}")
    results[p]['WordDistance'] = {}
    for i in range(0,11):
        wd_search_result = evaluate(ts_path, p, d_path, 'WordDistance', i)
        results[p]['WordDistance'][str(i)] = wd_search_result
     #   print(f"{p}: WordDistance {i} {wd_search_result}")
    dp_search_result = evaluate(ts_path, p, d_path, 'DependencyParsing')
    results[p]['DependencyParsing'] = dp_search_result
    #print(f"{p}: DependencyParsing {dp_search_result}")
print(json.dumps(results))

for alg in ['KeywordSearch', 'WordDistance', 'DependencyParsing']:
    print(f"Table for {alg}")
    for p in ['parallel', 'GPU', 'distributed']:
        if alg == 'WordDistance':
            for i in [0, 2, 5, 10]:
                print(
                    f"{p} & {str(i)} & {results[p][alg][str(i)]['TP']} & {results[p][alg][str(i)]['FP']} & {results[p][alg][str(i)]['TN']} & {results[p][alg][str(i)]['FN']}"
                    f"& {to_percentage(results[p][alg][str(i)]['Precision'])} & {to_percentage(results[p][alg][str(i)]['Recall'])} & {to_percentage(results[p][alg][str(i)]['Accuracy'])}",end='\\\\\\hline\n')
        else:
            print(
                f"{p} & {results[p][alg]['TP']} & {results[p][alg]['FP']} & {results[p][alg]['TN']} & {results[p][alg]['FN']}"
                f"& {to_percentage(results[p][alg]['Precision'])} & {to_percentage(results[p][alg]['Recall'])} & {to_percentage(results[p][alg]['Accuracy'])}", end='')
        print("\\\\\\hline")

