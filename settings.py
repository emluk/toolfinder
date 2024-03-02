import configparser

from DataAccess.Database import SQLiteConnector

config = configparser.ConfigParser()
config.read("D:\\Priv\\repository\\toolfinder\\toolfinder.ini")

db_connection = SQLiteConnector(config['db']['path'])
db_connection.connect()

max_parallel_requests = config['multithreading']['max_parallel_requests']