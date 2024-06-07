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

    def init_db(self, reset, noconfirm):
        if reset:
            if not noconfirm:
                response = input(f"This action will reset all tables in {self.db_file} - Do you want to proceed? [y/N]")
                if response.upper() != "Y":
                    print("Aborting")
                    sys.exit(-1)
            print(f"Resetting all tables in database {self.db_file}")
            self.connection.execute("pragma writable_schema = 1;")
            self.connection.execute("delete from sqlite_master where type in ('table', 'index', 'trigger');")
            self.connection.execute("pragma writable_schema = 0;")
            self.connection.commit()
            self.connection.execute("VACUUM;")
            self.connection.commit()
            self.connection.execute("pragma integrity_check;")
            self.connection.commit()
        # if self.connection is not None:
        #     self.connection.close()

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
        except Error as e:
            print(f"Connection to database failed with: {str(e)}")