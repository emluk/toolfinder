import configparser

from DataAccess.Database import SQLiteConnector

config = configparser.ConfigParser()
config.read("toolfinder.ini")

db_connection = SQLiteConnector(config['Paths']['db_file'])
db_connection.connect()

max_parallel_requests = config['Multithreading']['max_parallel_requests']