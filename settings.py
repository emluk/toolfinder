import configparser
import DataBase.DataAccess.SQLiteConnector


config = configparser.ConfigParser()
config.read(".\\toolfinder.ini")

db_connection = DataBase.DataAccess.SQLiteConnector.SQLiteConnector(config['db']['path'])
db_connection.connect()

max_parallel_requests = config['multithreading']['max_parallel_requests']