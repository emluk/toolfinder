#!/usr/bin/env python3
import argparse
import json
import re
import sys

import NLP.DataSet.DataSet
from NLP.Dictionary import Dictionary
from Search import Engine
from DataBase.DataAccess import BioToolsConnector, EDAMConnector
import settings
from DataBase.Loader import BioToolsLoader, EDAMLoader


def main():
    # read arguments from command line
    parser = argparse.ArgumentParser(prog="script")

    subparsers = parser.add_subparsers(dest="command")

    # subcommand for configuration customization
    config_parser = subparsers.add_parser('config')
    config_parser.add_argument('key', nargs="?", help="Option to configure. Format 'section.variable'")
    config_parser.add_argument('value', nargs="?", help="The value to set")
    config_parser.add_argument('--list', action='store_true', dest='list_options', help="Display current configuration")

    # subcommand for database initialization
    dbinit_parser = subparsers.add_parser('db-init')
    dbinit_parser.add_argument('--reset', action="store_true", dest="reset_db", default=False,
                               help="If set, the database will be reset completely")
    dbinit_parser.add_argument('--noconfirm', action="store_true", dest="noconfirm", default=False,
                               help="If set no prompt before deleting the database file is shown")

    # subcommand for retrieval of definitions
    retrieve_parser = subparsers.add_parser('load')
    retrieve_parser.add_argument('--all', action="store_true", dest="load_all",
                                 help="Retrieve all definitions (EDAM, biotools, synbiotools)")
    retrieve_parser.add_argument('definition', nargs="?", choices=["EDAM", "biotools", "synbiotools"])

    search_parser = subparsers.add_parser('search')
    search_parser.add_argument('--operation', action="append", required=False, dest="operation", default=[])
    search_parser.add_argument('--keyword', action="append", required=False, dest="keyword", default=[])
    search_parser.add_argument('-o', '--out-file', required=False, dest="out_file", default="")

    dataset_parser = subparsers.add_parser('dataset')
    dataset_sub_parsers = dataset_parser.add_subparsers(dest="dscommand")

    dataset_create_parser = dataset_sub_parsers.add_parser('create')
    dataset_create_parser.add_argument('--operation', action="append", required=False, dest="operation", default=[])
    dataset_create_parser.add_argument('--keyword', action="append", required=False, dest="keyword", default=[])
    dataset_create_parser.add_argument('-o', '--out-file', required=False, dest="out_file", default=None)

    dataset_label_parser = dataset_sub_parsers.add_parser('label')
    dataset_label_parser.add_argument('--file', required=True, dest="out_file")

    dataset_split_parser = dataset_sub_parsers.add_parser('split')
    dataset_split_parser.add_argument('--keyword', required=True, dest='split_property')
    dataset_split_parser.add_argument('--proportion', required=True, dest="split_proportion")
    dataset_split_parser.add_argument('--file', required=True, dest="split_in_file")
    dataset_split_parser.add_argument('--out-dir', required=True, dest="split_out_dir")

    dictionary_parser = subparsers.add_parser('dictionary')
    dict_sub_parsers = dictionary_parser.add_subparsers(dest="dictcommand")
    dict_create_parser = dict_sub_parsers.add_parser('create')
    dict_create_parser.add_argument('--keyword', required=True, dest="keywords")
    dict_create_parser.add_argument("--property", dest='property', required=True)
    dict_create_parser.add_argument("--file", dest="file", required=True)
    dict_create_parser.add_argument("--out-file", dest="out_file", required=True)
    args = parser.parse_args()


    # validate arguments and dispatch action

    # dispatch action
    if args.command == 'load':
        if not validate_load_args(args):
            retrieve_parser.print_help()
            return -1
        dispatch_load(args.load_all, args.definition)
    elif args.command == 'db-init':
        settings.db_connection.init_db(args.reset_db, args.noconfirm)
        EDAMConnector.create_edam_table()
        EDAMConnector.create_edam_operations_structure_table()
        BioToolsConnector.create_biotools_tables()
    elif args.command == 'config':
        if not args.list_options:
            if args.key is None or args.value is None:
                print("Missing value")
                config_parser.print_help()
                sys.exit(-1)
            key_regex = re.compile(r'^([a-zA-Z]+\.)([a-zA-Z]+_)*([a-zA-Z]+)$')
            if not key_regex.match(args.key):
                print("Invalid format")
                config_parser.print_help()
                sys.exit(-1)
            configure(args.key, args.value)
        else:
            print_configuration()
    elif args.command == 'search':
        result = Engine.search_tools(args.operation, args.keyword)
        if args.out_file == "":
            print(result)
        else:
            with open(args.out_file, 'w') as of:
                json.dump(result, of)
    elif args.command == 'dataset':
        if args.dscommand == 'create':
            NLP.DataSet.DataSet.create(args.operation, args.keyword, args.out_file)
        elif args.dscommand == 'label':
            NLP.DataSet.DataSet.LabellingTool(args.out_file, args.out_file)
        elif args.dscommand == 'split':
            NLP.DataSet.DataSet.split(args.split_property, args.split_proportion, args.split_in_file, args.split_out_dir)
    elif args.command == 'dictionary':
        if args.dictcommand == 'create':
            NLP.Dictionary.Dictionary.create(args.keywords, args.property, args.file, args.out_file)
    else:
        print(f"Invalid command {args.command}")


def print_configuration():
    for section in list(settings.config.keys()):
        for item in list(settings.config[section].keys()):
            print(f"{section}.{item}={settings.config[section][item]}")


def configure(key, value):
    parts = key.split('.')
    item = parts[-1]
    sections = key.replace(f".{item}", "")

    if not settings.config.has_section(sections):
        print(f"Configuration does not contain the section '{sections}'")
        sys.exit(-1)
    try:
        _ = settings.config[sections][item]
    except KeyError:
        print(f"Section {sections} does not contain a variable named '{item}'")
    settings.config[sections][item] = value
    with open('toolfinder.ini', 'w') as config_file:
        settings.config.write(config_file)



def dispatch_load(load_all, definition):
    if load_all:
        EDAMLoader.load()
        BioToolsLoader.load()
        # rest of the definitions here
        return
    dispatch_map = {
        "EDAM": EDAMLoader.load,
        "biotools": BioToolsLoader.load
    }
    dispatch_map[definition]()


def validate_load_args(args):
    # load command
    if not args.load_all and args.definition is None:
        print("If --all is not set, the definition to load is required.")
        return False
    return True


if __name__ == '__main__':
    main()
