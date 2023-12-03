import configparser

from DataAccess.Database import SQLiteConnector

config = configparser.ConfigParser()
config.read("toolfinder.ini")

db_connection = SQLiteConnector(config['paths']['db_file'])
db_connection.connect()

max_parallel_requests = config['multithreading']['max_parallel_requests']