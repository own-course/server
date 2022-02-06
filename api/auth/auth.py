from flask_restx import Resource
from util.dto import AuthDto
from flask_mail import Mail, Message
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)
from database.database import Database
import bcrypt
import random
import configparser

auth = AuthDto.api
_model_auth_email = AuthDto.model_auth_email
_model_email = AuthDto.model_email
_auth_email_response = AuthDto.auth_email_response
_auth_email_response_with_code = AuthDto.auth_email_response_with_code
_auth_response_with_token = AuthDto.auth_response_with_token
_auth_response_with_refresh_token = AuthDto.auth_response_with_refresh_token

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))


@auth.route('/email')
@auth.response(200, 'Success', _auth_email_response_with_code)
class EmailAuthAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('email', type=str, required=True)
        args = parser.parse_args()

        self.email = args['email']
        self.code = random.randint(100000, 999999)

    @auth.expect(_model_auth_email)
    def post(self):
        """이메일 인증코드 전송"""
        msg = Message('OwnCourse 회원가입 인증 메일입니다.',
                      sender='owncourse2021@gmail.com',
                      recipients=[self.email])
        msg.body = f'인증코드 : {self.code}'
        mail = Mail()
        mail.send(msg)

        return {'message': 'Email is sent successfully.',
                'code': self.code}, 200


@auth.route('/signup')
@auth.response(200, 'Success', _auth_response_with_refresh_token)
class SignUpAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        self.email = args['email']
        self.password = bcrypt.hashpw(args['password'].encode("utf-8"), bcrypt.gensalt())

    @auth.expect(_model_email)
    def post(self):
        """이메일 회원가입"""
        database = Database()
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

        sql = """
            SELECT LAST_INSERT_ID() as id;
        """
        id = database.execute_one(sql)
        sql = """
            INSERT INTO Profile (user_id) VALUES (%(user_id)s)
        """
        database.execute(sql, {'user_id': id['id']})
        database.commit()
        database.close()

        return get_token(id['id']), 200


@auth.route('/signin')
@auth.response(200, 'Success', _auth_response_with_refresh_token)
@auth.response(400, 'Bad Request', _auth_email_response)
class SignInAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()

        self.email = args['email']
        self.password = args['password']

    @auth.expect(_model_email)
    def post(self):
        """이메일 로그인"""
        database = Database()
        value = {
            'email': self.email
        }
        sql = """
            SELECT * FROM User
            WHERE email = %(email)s AND platform_type = 'Email'
            """
        row = database.execute_one(sql, value)
        database.close()

        if row is not None:
            if bcrypt.checkpw(self.password.encode('utf-8'), row['password'].encode('utf-8')):
                return get_token(row['id']), 200
            else:
                return {'message': 'Password does not match.'}, 400
        else:
            return {'message': 'User does not exist.'}, 400


@auth.route('/token/refresh')
@auth.response(200, 'Success', _auth_response_with_token)
@auth.response(401, 'Unauthorized')
class TokenAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @jwt_required(refresh=True)
    @auth.doc(security='apiKey')
    def get(self):
        """resfresh token으로 access token 갱신"""
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        resp = {'access_token': access_token}

        return resp, 200


def get_token(user):
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    resp = {'access_token': access_token, 'refresh_token': refresh_token}

    return resp
