#!/usr/bin/env python3
import argparse
import json
import re
import sys

import Label.Labeling
import NLP.DataSet.DataSet
import settings
from DataBase.DataAccess import BioToolsConnector, EDAMConnector
from DataBase.Loader import BioToolsLoader, EDAMLoader
from NLP.Dictionary import Dictionary
from Search import Engine
from Utility.Print import print_list_in_columns


def main():
    # read arguments from command line
    parser = argparse.ArgumentParser(prog="toolfinder")

    subparsers = parser.add_subparsers(dest="command")

    # command for configuration customization
    config_parser = subparsers.add_parser('config', help="Command to configure any values in the toolfinder.ini file."
                                                         "Requires the format 'section.variable'.")
    config_parser.add_argument('key', nargs="?", help="Option to configure. Format 'section.variable'")
    config_parser.add_argument('value', nargs="?", help="The value to set")
    config_parser.add_argument('--list', action='store_true', dest='list_options', help="Display current configuration")

    # command for database initialization
    dbinit_parser = subparsers.add_parser('db-init',
                                          help="Initialize the database required for toolfinder with all tables.")
    dbinit_parser.add_argument('--reset', action="store_true", dest="reset_db", default=False,
                               help="If set, the database will be reset completely")
    dbinit_parser.add_argument('--no-confirm', action="store_true", dest="noconfirm", default=False,
                               help="If set no prompt before deleting the database file is shown")

    # command for retrieval of definitions
    retrieve_parser = subparsers.add_parser('load', help="Load EDAM and BioTools into the database.")
    retrieve_parser.add_argument('--all', action="store_true", dest="load_all",
                                 help="Retrieve all definitions (EDAM, biotools)")
    retrieve_parser.add_argument('definition', nargs="?", choices=["EDAM", "biotools"],
                                 help="The remote repository to pull. Possible values are EDAM and biotools")

    # command for searching tools
    search_parser = subparsers.add_parser('search',
                                          help="Search for tools and filtering the results based on different criteria."
                                               "If an output file path is given, the array of tools is written to that file. Otherwise it is written to stdout.")
    search_parser.add_argument('--operation', action="append", required=False, dest="operation", default=[],
                               help="EDAM operation to filter tools by. Can be repeated. "
                                    "The EDAM operation can be set by name (e.g. Analysis), or by the EDAM id (e.g. operation_2945)"
                                    "To allow all children of an operation use child(op id)."
                                    "To allow all descendants of an operation use sub(op id).")
    search_parser.add_argument('--keyword', action="append", required=False, dest="keyword", default=[],
                               help="A keyword to filter tools by. Can be repeated."
                                    "If the keyword is in the description of the tool, it is included in the result.")
    search_parser.add_argument('--input', action='append', required=False, dest='input', default=[], help="Input data and format to filter tools by. Can be repeated."
                                                                                                          "To search for data and format, provide 'data:format' with either EDAM Ids, or Names."
                                                                                                          "To search for only one of them, just provide the name or EDAM id")
    search_parser.add_argument('--output', action='append', required=False, dest='output', default=[],
                               help="Output data and format to filter tools by. Can be repeated."
                                    "To search for data and format, provide 'data:format' with either EDAM Ids, or Names."
                                    "To search for only one of them, just provide the name or EDAM id")
    search_parser.add_argument('--label', action="append", required=False, dest="label", default=[], help='Labels that should be present for the tool')
    search_parser.add_argument('-o', '--out-file', required=False, dest="out_file", default="",
                               help="Path to a file to store the result in. If left empty, result will be printed to stdout.")

    # command for finding compatible tools
    find_parser = subparsers.add_parser('find', help="Find compatible tools")
    find_sub_parsers = find_parser.add_subparsers(dest='findcommand')
    suc_parser = find_sub_parsers.add_parser('successor')
    suc_parser.add_argument('tool', help="The name or ID of the tool")
    suc_parser.add_argument('--operation', action="append", required=False, dest="operation", default=[], help="Operation the successor should perform")
    suc_parser.add_argument('--label', action="append", required=False, dest="label", default=[], help="Labels that should be present for the successor tool")
    pre_parser = find_sub_parsers.add_parser('predecessor')
    pre_parser.add_argument('tool', help="The name or ID of the tool")
    pre_parser.add_argument('--operation', action="append", required=False, dest="operation", default=[],
                            help="Operation the predecessor should perform")
    pre_parser.add_argument('--label', action="append", required=False, dest="label", default=[],
                            help="Labels that should be present for the predecessor tool")
    rep_parser = find_sub_parsers.add_parser('replacement', help="Find a replacement for a tool")
    rep_parser.add_argument('tool', help="The name or ID of the tool")
    rep_parser.add_argument('--label', action="append", required=False, dest="label", default=[],
                            help="Labels that should be present for the predecessor tool")

    # command for creating and handling datasets
    dataset_parser = subparsers.add_parser('dataset',
                                           help="Create and manipulate datasets from data available in the database.")
    dataset_sub_parsers = dataset_parser.add_subparsers(dest="dscommand")

    dataset_create_parser = dataset_sub_parsers.add_parser('create',
                                                           help="Create a dataset from the database using the search functionality.")
    dataset_create_parser.add_argument('--operation', action="append", required=False, dest="operation", default=[],
                                       help="EDAM operation to filter tools by. Can be repeated. "
                                            "The EDAM operation can be set by name (e.g. Analysis), or by the EDAM id (e.g. operation_2945)"
                                            "To allow all children of an operation use child(op id)."
                                            "To allow all descendants of an operation use sub(op id).")
    dataset_create_parser.add_argument('--keyword', action="append", required=False, dest="keyword", default=[],
                                       help="A keyword to filter tools by. Can be repeated."
                                            "If the keyword is in the description of the tool, it is included in the result.")
    dataset_create_parser.add_argument('--input', action='append', required=False, dest='input', default=[],
                               help="Input data and format to filter tools by. Can be repeated."
                                    "To search for data and format, provide 'data:format' with either EDAM Ids, or Names."
                                    "To search for only one of them, just provide the name or EDAM id")
    dataset_create_parser.add_argument('--output', action='append', required=False, dest='output', default=[],
                               help="Output data and format to filter tools by. Can be repeated."
                                    "To search for data and format, provide 'data:format' with either EDAM Ids, or Names."
                                    "To search for only one of them, just provide the name or EDAM id")
    dataset_create_parser.add_argument('--label', action="append", required=False, dest="label", default=[],
                               help='Labels that should be present for the tool')
    dataset_create_parser.add_argument('-o', '--out-file', required=False, dest="out_file", default=None,
                                       help="Path to a file to store the result in. If left empty, result will be printed to stdout.")

    dataset_label_parser = dataset_sub_parsers.add_parser('label', help="Simple GUI to label a dataset from a file. "
                                                                        "Please create a backup of the dataset before starting."
                                                                        "The file contents are being overwritten on save")
    dataset_label_parser.add_argument('file',
                                      help="Path to the file containing the dataset. Will be overwritten on save!")

    dataset_split_parser = dataset_sub_parsers.add_parser('split', help="Split a dataset into a training and test set.")
    dataset_split_parser.add_argument('--property', required=True, dest='split_property',
                                      help="Property in the dataset to split the dataset by.")
    dataset_split_parser.add_argument('--proportion', required=True, dest="split_proportion",
                                      help="Number between 0 and 1")
    dataset_split_parser.add_argument('--file', required=True, dest="split_in_file",
                                      help="Path to the file containing the dataset to split.")
    dataset_split_parser.add_argument('--out-dir', required=True, dest="split_out_dir",
                                      help="Path to the directory to save the results. Results will be split into multiple files.")

    # command for creating dictionaries
    dictionary_parser = subparsers.add_parser('dictionary', help="Create dictionaries from the database.")
    dict_sub_parsers = dictionary_parser.add_subparsers(dest="dictcommand")
    dict_create_parser = dict_sub_parsers.add_parser('create',
                                                     help="Create a dictionary from a labeled dataset using the search functionality.")
    dict_create_parser.add_argument('--keyword', required=True, dest="keywords",
                                    help="Keyword to find related words to.")
    dict_create_parser.add_argument("--property", dest='property', required=True,
                                    help="Property that must be true to consider a keyword relevant.")
    dict_create_parser.add_argument("--file", dest="file", required=True, help="Path to the labeled dataset.")
    dict_create_parser.add_argument("--out-file", dest="out_file", required=True,
                                    help="Path to store the created dictionary.")

    # sub command for labelling
    label_parser = subparsers.add_parser('label',
                                         help="Label tools in the database with a chosen algorithm and dictionary")
    label_sub_parsers = label_parser.add_subparsers(dest="labelcommand")
    label_assign_parser = label_sub_parsers.add_parser('assign', help='Manually assign a label to a tool')
    label_assign_parser.add_argument('--tool', required=True, action="append", dest="tools", help="Tool(s) to assign the label to")
    label_assign_parser.add_argument('--label', required=True, help="Label to assign to the tool(s)")

    label_remove_parser = label_sub_parsers.add_parser('remove', help='Remove a label from a tool')
    label_remove_parser.add_argument('--label', required=True, help="Label to remove.")
    label_remove_parser.add_argument('--tool', required=True, action="append", dest="tools", help="Tool(s) to remove the label from")

    label_remove_all_parser = label_sub_parsers.add_parser('remove-all', help='Remove all labels from a tool')
    label_remove_all_parser.add_argument('--no-confirm', required=False, dest='no_confirm', action="store_true", help="If set, no confirmation is needed to proceed.")

    label_all_parser = label_sub_parsers.add_parser('all', help="Label all tools in the database")
    algorithm_group = label_all_parser.add_mutually_exclusive_group(required=True)
    algorithm_group.add_argument('--KeywordSearch', '--kws', action="store_true", help="Use keyword search algorithm")
    algorithm_group.add_argument('--WordDistance', '--wd', action="store_true", help="Use word distance algorithm")
    algorithm_group.add_argument('--DependencyParsing', '--dp', action="store_true", help="Use dependency parsing algorithm")
    label_all_parser.add_argument('--label', required=True, help="Label to assign.")
    label_all_parser.add_argument('--dictionary', required=True, help="Path to the file containing the dictionary")
    label_all_parser.add_argument('--max_distance', dest='max_distance', help="The allowed distance between words. Only relevant for WordDistance algorithm")

    # label_automatic_parser.add_argument()
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
        result = Engine.search_tools(args.operation, args.keyword, args.input, args.output, args.label)
        if args.out_file == "":
            print_list_in_columns(result)
        else:
            with open(args.out_file, 'w') as of:
                json.dump(result, of)
    elif args.command == 'find':
        if args.findcommand == 'successor':
            print_list_in_columns(Engine.find_compatible_successors(args.tool, args.operation, args.label))
        elif args.findcommand == 'predecessor':
            print_list_in_columns(Engine.find_compatible_predecessors(args.tool, args.operation, args.label))
        elif args.findcommand == 'replacement':
            print_list_in_columns(Engine.find_replacement(args.tool, args.label))
    elif args.command == 'dataset':
        if args.dscommand == 'create':
            NLP.DataSet.DataSet.create(args.operation, args.keyword, args.input, args.output, args.label, args.out_file)
        elif args.dscommand == 'label':
            NLP.DataSet.DataSet.LabellingTool(args.file, args.file)
        elif args.dscommand == 'split':
            NLP.DataSet.DataSet.split(args.split_property, args.split_proportion, args.split_in_file,
                                      args.split_out_dir)
    elif args.command == 'dictionary':
        if args.dictcommand == 'create':
            NLP.Dictionary.Dictionary.create(args.keywords, args.property, args.file, args.out_file)
    elif args.command == 'label':
        if args.labelcommand == 'assign':
            Label.Labeling.assign(args.tools, args.label)
        elif args.labelcommand == 'remove':
            Label.Labeling.remove(args.tools, args.label)
        elif args.labelcommand == 'remove-all':
            if not args.no_confirm:
                usr = input("This will remove all labels from the database. Do you want to proceed? [y/N]")
                if usr.lower() != 'y':
                    print(f"Abort")
                    sys.exit(0)
                Label.Labeling.clear_all()
        elif args.labelcommand == 'all':
            if args.KeywordSearch:
                algorithm = 'KeywordSearch'
                Label.Labeling.label_all(algorithm, args.dictionary, args.label, None)
            if args.WordDistance:
                algorithm = 'WordDistance'
                Label.Labeling.label_all(algorithm, args.dictionary, args.label, int(args.max_distance))
            if args.DependencyParsing:
                algorithm = 'DependencyParsing'
                Label.Labeling.label_all(algorithm, args.dictionary, args.label, None)
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
