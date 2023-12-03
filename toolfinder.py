#!/usr/bin/env python3
import argparse
import re
import sys

import settings
from Repository import EDAMConnector, BioToolsConnector


def main():
    # read arguments from command line
    parser = argparse.ArgumentParser(prog="script")

    subparsers = parser.add_subparsers(dest="command")

    # subcommand for configuration customization
    config_parser = subparsers.add_parser('config')
    config_parser.add_argument('key', help="Option to configure. Format 'section.variable'")
    config_parser.add_argument('value', help="The value to set")

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
    elif args.command == 'config':
        key_regex = re.compile(r'^([a-zA-Z]+\.)([a-zA-Z]+_)*([a-zA-Z]+)$')
        if not key_regex.match(args.key):
            print("Invalid format")
            config_parser.print_help()
            sys.exit(-1)
        configure(args.key, args.value)
    else:
        print(f"Invalid command {args.command}")


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
        EDAMConnector.load()
        BioToolsConnector.load()
        # rest of the definitions here
        return
    dispatch_map = {
        "EDAM": EDAMConnector.load,
        "biotools": BioToolsConnector.load
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
