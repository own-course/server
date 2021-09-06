from flask import Flask
import configparser

app = Flask(__name__)

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))

if __name__ == '__main__':
    app.run('0.0.0.0', debug=config['DEFAULT']['DEBUG'], port=config['DEFAULT']['PORT'])