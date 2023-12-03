import os
import sqlite3
import sys
from sqlite3 import Error


class SQLiteConnector:
    def __init__(self, db_file):
        self.connection = None
        self.db_file = db_file

    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    def create_edam_table(self):
        print("Initializing EDAM table...", end=" ")
        try:
            self.connection.execute('''create table EDAM
                                        (
                                            EDAM_id       TEXT not null
                                                constraint EDAM_pk
                                                    primary key,
                                            EDAM_category TEXT,
                                            EDAM_url      TEXT,
                                            Name          TEXT not null,
                                            Definition    TEXT,
                                            Synonyms      TEXT,
                                            Obsolete      INT  not null,
                                            Parents       TEXT
                                        );
                                            ''')
        except Error as e:
            print(f"Error: {str(e)}")
            return
        print("Done")

    def create_biotools_info_table(self):
        print("Initializing biotools_tools_info...", end=" ")
        try:
            self.connection.execute('''create table biotools_tools_info
                                        (
                                            Biotools_id    TEXT not null
                                                constraint biotools_tools_pk
                                                    primary key,
                                            Biotools_CURIE TEXT,
                                            Version        TEXT,
                                            Name           TEXT not null,
                                            Description    TEXT,
                                            Homepage       TEXT,
                                            Documentation  TEXT,
                                            Published      TEXT,
                                            LastUpdate     TEXT
                                        );

            ''')
        except Error as e:
            print(f"Error: {str(e)}")
            return
        print("Done")

    def create_biotools_operations_table(self):
        print("Intializing biotools_tools_operations")
        try:
            self.connection.execute('''create table biotools_tools_operations
                                        (
                                            Biotools_id TEXT    not null
                                                constraint biotools_tools_operations_biotools_tools_info_Biotools_id_fk
                                                    references biotools_tools_info,
                                            EDAM_id     integer not null
                                                constraint biotools_tools_operations_EDAM_EDAM_id_fk
                                                    references EDAM,
                                            constraint biotools_tools_operations_pk
                                                primary key (Biotools_id, EDAM_id)
                                        );
                                        ''')
        except Error as e:
            print(f"Error: {str(e)}")
            return
        print("Done")

    def create_biotools_topics_table(self):
        print("Intializing biotools_tools_topics")
        try:
            self.connection.execute('''create table biotools_tools_topics
                                        (
                                            Biotools_id TEXT not null
                                                constraint biotools_tools_topics_biotools_tools_info_Biotools_id_fk
                                                    references biotools_tools_info,
                                            EDAM_id     TEXT not null
                                                constraint biotools_tools_topics_EDAM_EDAM_id_fk
                                                    references EDAM,
                                            constraint biotools_tools_topics_pk
                                                primary key (Biotools_id, EDAM_id)
                                        );
                                        ''')
        except Error as e:
            print(f"Error: {str(e)}")
            return
        print("Done")

    def create_biotools_tools_collection(self):
        print("Intializing biotools_tools_collection")
        try:
            self.connection.execute('''create table biotools_tools_topics
                                                (
                                                    Biotools_id TEXT not null
                                                        constraint biotools_tools_topics_biotools_tools_info_Biotools_id_fk
                                                            references biotools_tools_info,
                                                    EDAM_id     TEXT not null
                                                        constraint biotools_tools_topics_EDAM_EDAM_id_fk
                                                            references EDAM,
                                                    constraint biotools_tools_topics_pk
                                                        primary key (Biotools_id, EDAM_id)
                                                );
                                                ''')
        except Error as e:
            print(f"Error: {str(e)}")
            return
        print("Done")

    def create_biotools_tables(self):
        self.create_biotools_info_table()
        self.create_biotools_operations_table()
        self.create_biotools_topics_table()

    def init_db(self, reset, noconfirm):
        if reset:
            if not noconfirm:
                response = input(f"This action will delete the entire database in {self.db_file} - Do you want to proceed? [y/N]")
                if response.upper() != "Y":
                    print("Aborting")
                    sys.exit(-1)
            print(f"Deleting database at {self.db_file}")
            self.connection.close()
            os.remove(self.db_file)
            self.connect()
        self.create_edam_table()
        self.create_biotools_tables()
        if self.connection is not None:
            self.connection.close()

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
        except Error as e:
            print(f"Connection to database failed with: {str(e)}")

    @staticmethod
    def escape_input(value):
        value = value.replace('"', "'")
        return value

    def insert_edam(self, rows):
        for row in rows:
            obsolete_int = 0
            if row["obsolete"]:
                obsolete_int = 1
            for key in list(row.keys()):
                if key != "obsolete":
                    row[key] = self.escape_input(str(row[key]))
            self.connection.execute(f'''insert into EDAM (EDAM_id, EDAM_category, EDAM_url, Name, Definition, Synonyms, Obsolete, Parents)
                                        values ("{row["edam_id"]}", "{row["edam_category"]}","{row["edam_url"]}", "{row["name"]}", "{row["definition"]}", "{row["synonyms"]}", {obsolete_int}, "{row["parents"]}")
                                        on conflict do nothing;
                                    ''')
        self.connection.commit()


    def insert_biotools(self, items):
        for item in items:
            biotools_id = item['biotoolsID']
            try:
                version = item['version'][0]
            except Exception:
                version = None
            biotools_curie = item['biotoolsCURIE']
            name = item['name']
            description = self.escape_input(item['description'])
            homepage = item['homepage']
            try:
                docs = item['documentation'][0]['url']
            except Exception:
                docs = None
            published = item['additionDate']
            updated = item['lastUpdate']
            try:
                self.connection.execute(f'''insert into biotools_tools_info (Biotools_id, Version, Biotools_CURIE, Name, Description, Homepage, Documentation,
                                                     Published, LastUpdate)
                                                    values ("{biotools_id}", "{version}", "{biotools_curie}", "{name}", "{description}", "{homepage}", "{docs}", "{published}", "{updated}")
                                                    on conflict do nothing;
                            ''')
            except Error as e:
                print(f"Entry '{biotools_id}' caused error '{str(e)}'")

            for i in range(0, len(item['function'])): #TODO: add input and output here if available
                for op in item['function'][i]['operation']:
                    edam_id = op['uri'].split("/")[-1]
                    try:
                        self.connection.execute(f'''insert into biotools_tools_operations (Biotools_id, EDAM_id)
                                                    values("{biotools_id}", "{edam_id}") on conflict do nothing
                        ''')
                    except Error as e:
                        print(f"Entry '{biotools_id}' caused error '{str(e)}'")

            for topic in item['topic']:
                edam_id = topic['uri'].split("/")[-1]
                try:
                    self.connection.execute(f'''insert into biotools_tools_topics (Biotools_id, EDAM_id)
                                                values("{biotools_id}", "{edam_id}") on conflict do nothing
                    ''')
                except Error as e:
                    print(f"Entry '{biotools_id}' caused error '{str(e)}'")

        self.connection.commit()