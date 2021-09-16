import pymysql
import configparser

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))

class Database:
    def __init__(self):
        self.db = pymysql.connect(
            host=config['DATABASE']['HOST'],
            user=config['DATABASE']['USER'],
            password=config['DATABASE']['PASSWORD'],
            db=config['DATABASE']['DB'],
            port=int(config['DATABASE']['PORT']),
            charset=config['DATABASE']['CHARSET']
        )
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def execute(self, query, args={}):
        self.cursor.execute(query, args)

    def execute_one(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row

    def execute_all(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.db.commit()