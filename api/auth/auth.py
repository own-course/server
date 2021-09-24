from flask_restx import Namespace, Resource, fields
from flask_mail import Mail, Message
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from database.database import Database
import bcrypt
import random
import configparser

auth = Namespace('Auth', description='이메일 회원가입 및 로그인')

model_auth_email = auth.model('model_auth_email', {
    'email': fields.String(description='Email'),
})
model_email = auth.model('model_email', {
    'email': fields.String(description='Email'),
    'password': fields.String(description='비밀번호')
})

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))

database = Database()

@auth.route('/email')
@auth.doc(responses={200: 'Success'})
class EmailAuthAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()

        self.email = args['email']
        self.code = random.randint(100000, 999999)

    @auth.expect(model_auth_email)
    def post(self):
        """이메일 인증코드 전송"""
        msg = Message('OwnCourse 회원가입 인증 메일입니다.',
                      sender='owncourse2021@gmail.com',
                      recipients=[self.email])
        msg.body = f'인증코드 : {self.code}'
        mail = Mail()
        mail.send(msg)

        return {'result': True, 'message': 'Email is sent successfully.',
                'code': self.code}, 200

@auth.route('/signup')
@auth.doc(responses={200: 'Success'})
class SignUpAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        self.email = args['email']
        self.password = bcrypt.hashpw(args['password'].encode("utf-8"), bcrypt.gensalt())

    @auth.expect(model_email)
    def post(self):
        """이메일 회원가입"""
        value = {
            'email': self.email,
            'password': self.password.decode('utf-8'),
            'platform_type': 'Email'
        }
        sql = """
            INSERT INTO User (platform_type, email, password)
            VALUES (%(platform_type)s, %(email)s, %(password)s)
        """
        database.execute(sql, value)
        database.commit()
        return {'result': True}, 200

@auth.route('/signin')
@auth.doc(responses={200: 'Success'})
@auth.doc(responses={400: 'Bad Request'})
class SignInAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        self.email = args['email']
        self.password = args['password']

    @auth.expect(model_email)
    def post(self):
        """이메일 로그인"""
        value = {
            'email': self.email
        }
        sql = """
            SELECT * FROM User
            WHERE email = %(email)s AND platform_type = 'Email'
            """
        row = database.execute_one(sql, value)

        if row is not None:
            if bcrypt.checkpw(self.password.encode('utf-8'), row['password'].encode('utf-8')):
                return get_token(row['id']), 200
            else:
                return {'result': False, 'message': 'Password does not match.'}, 400
        else:
            return {'result': False, 'message': 'User does not exist.'}, 400

@auth.route('/token/refresh')
@auth.doc(responses={200: 'Success'})
@auth.doc(responses={401: 'Unauthorized'})
class TokenAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @jwt_required(refresh=True)
    @auth.doc(security='apiKey')
    def get(self):
        """resfresh token으로 access token 갱신"""
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        resp = {'result': True, 'access_token': access_token}

        return resp, 200

def get_token(user):
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    resp = {'result': True, 'access_token': access_token, 'refresh_token': refresh_token}

    return resp