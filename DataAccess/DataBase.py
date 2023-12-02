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
            print("EDAM Table initialized")
        except Error as e:
            print(e)
        finally:
            if self.connection is not None:
                self.connection.close()

    def connect(self):
        try:
            self.connection = sqlite3.connect(r"D:\Priv\repository\toolfinder\Data\test.db")
        except Error as e:
            print(f"Connection to database failed with: {e}")

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
            print(f"""insert into EDAM (EDAM_id, EDAM_category, EDAM_url, Name, Definition, Synonyms, Obsolete, Parents)
                                        values ("{row["edam_id"]}", "{row["edam_category"]}","{row["edam_url"]}", "{row["name"]}", "{row["definition"]}", "{row["synonyms"]}", {obsolete_int}, "{row["parents"]}")
                                    """)
            self.connection.execute(f'''insert into EDAM (EDAM_id, EDAM_category, EDAM_url, Name, Definition, Synonyms, Obsolete, Parents)
                                        values ("{row["edam_id"]}", "{row["edam_category"]}","{row["edam_url"]}", "{row["name"]}", "{row["definition"]}", "{row["synonyms"]}", {obsolete_int}, "{row["parents"]}")
                                    ''')
        self.connection.commit()
