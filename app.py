from flask import Flask
from flask_restx import Api
from api.auth.auth import auth
from api.auth.oauth import oauth
from api.review.review import review
from flask_mail import Mail
from flask_jwt_extended import JWTManager
import configparser

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))

app = Flask(__name__)
authorizations = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}
api = Api(app, authorizations=authorizations)

app.config['MAIL_SERVER'] = config['MAIL']['MAIL_SERVER']
app.config['MAIL_PORT'] = config['MAIL']['MAIL_PORT']
app.config['MAIL_USERNAME'] = config['MAIL']['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = config['MAIL']['MAIL_PASSWORD']
app.config['MAIL_USE_SSL'] = config['MAIL']['MAIL_USE_SSL']

app.config['JWT_SECRET_KEY'] = config['JWT']['JWT_SECRET_KEY']

jwt = JWTManager(app)
mail = Mail(app)

api.add_namespace(auth, '/auth')
api.add_namespace(oauth, '/oauth')
api.add_namespace(review, '/review')

if __name__ == '__main__':
    app.run(config['DEFAULT']['HOST'], debug=config['DEFAULT']['DEBUG'], port=config['DEFAULT']['PORT'])