from flask import Flask
from flask_restx import Api
from api.auth.auth import auth
from api.auth.oauth import oauth
from api.user.user import user
from api.place.place import place
from api.review.review import review
from api.course.course import course
from flask_mail import Mail
from flask_jwt_extended import JWTManager
import configparser
import datetime

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
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=int(config['JWT']['JWT_ACCESS_TOKEN_EXPIRES']))

jwt = JWTManager(app)
mail = Mail(app)

api.add_namespace(auth, '/auth')
api.add_namespace(oauth, '/oauth')
api.add_namespace(user, '/user')
api.add_namespace(place, '/place')
api.add_namespace(review, '/review')
api.add_namespace(course, '/course')

if __name__ == '__main__':
    app.run(config['DEFAULT']['HOST'], debug=config['DEFAULT']['DEBUG'], port=config['DEFAULT']['PORT'])