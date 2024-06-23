import sys


def print_list_in_columns(l):
    if l is None or len(l) == 0:
        print()
        sys.exit(0)
    res_list = sorted(l)
    for item in res_list:
        print(item)
