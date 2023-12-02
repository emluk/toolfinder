import sqlite3
from sqlite3 import Error


class SQLiteConnector:
    def __init__(self):
        self.connection = None

    def __del__(self):
        if self.connection is not None:
            self.connection.close()
            print("Connection to database closed")

    def create_db(self):
        try:
            self.connection = sqlite3.connect(r"D:\Priv\repository\BA-Code\Data\test.db")
            print("Databasefile created")
            self.connection.execute('''create table EDAM
                                        (
                                            EDAM_id       TEXT not null
                                                constraint EDAM_pk
                                                    primary key,
                                            EDAM_category TEXT,
                                            Name          TEXT not null,
                                            Definition    TEXT,
                                            Synonyms      TEXT,
                                            Obsolete      INT  not null,
                                            Parents       TEXT
                                        );
                                        ''')
            print("EDAM Table initialized")
        except Error as e:
            print(e)
        finally:
            if self.connection is not None:
                self.connection.close()

    def connect(self):
        try:
            self.connection = sqlite3.connect(r"D:\Priv\repository\BA-Code\Data\test.db")
        except Error as e:
            print(f"Connection to database failed with: {e}")


    def insert_EDAM(self, edam_id, edam_category, name, definition, synonyms, obsolete, parents):
        obsolete_int = 0
        if obsolete:
            obsolete_int = 1
        self.connection.execute(f'''insert into EDAM (edam_id, EDAM_category, Name, Definition, Synonyms, Obsolete, Parents)
                                    values ('{edam_id}', '{edam_category}', '{name}', '{definition}', '{synonyms}', {obsolete_int}, '{parents}')
                                ''')
        self.connection.commit()