from flask import make_response
from flask_restx import Namespace, Resource, fields
from api.auth.auth import get_token
from database.database import Database
import requests
import configparser

oauth = Namespace('OAuth', description='카카오, 네이버, 구글 로그인')

model_kakao_auth = oauth.model('model_kakao_auth', {
    'code': fields.String(description='Kakao authorization code')
})
model_naver_auth = oauth.model('model_naver_auth', {
    'code': fields.String(description='Naver authorization code'),
    'state': fields.String(description='Naver state')
})
model_google_auth = oauth.model('model_google_auth', {
    'code': fields.String(description='Google authorization code')
})

config = configparser.ConfigParser()
config.read_file(open('config/config.ini'))

host = config['DEFAULT']['HOST']
port = config['DEFAULT']['PORT']

database = Database()

@oauth.route('/kakao')
class KakaoLoginAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('code', type=str, required=True)
        args = parser.parse_args()

        self.code = args['code']

    @oauth.expect(model_kakao_auth)
    def post(self):
        """Kakao 로그인"""
        token_json = requests.post(
            url="https://kauth.kakao.com/oauth/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "client_id": config['KAKAO_API']['CLIENT_ID'],
                "redirect_uri": f"http://{host}:{port}/oauth/kakao",
                "code": self.code,
            },
        ).json()
        error = token_json.get("error", None)
        if error is not None:
            return make_response({"message": "INVALID_CLIENT"}, 400)

        access_token = token_json['access_token']
        user_info = requests.post(
            url="https://kapi.kakao.com/v2/user/me",
            headers={
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": f"Bearer {access_token}"
            }
        ).json()

        sql1 = f"SELECT * FROM User " \
               f"WHERE platform_type = 'Kakao' AND platform_id = {user_info['id']}"
        row = database.execute_one(sql1)
        if row is None:
            platform_id = user_info['id']
            email = user_info['kakao_account']['email']
            sql2 = f"INSERT INTO User (platform_type, email, platform_id)" \
                  f"VALUES ('Kakao', {email}, {platform_id})"
            database.execute(sql2)
            database.commit()

            row = database.execute_one(sql1)
            user = row['id']
            name = user_info['kakao_account']['profile']['nickname']
            profile_image = user_info['kakao_account']['profile']['profile_image_url']
            gender = user_info['kakao_account']['gender']
            sql = f"INSERT INTO Profile (id, name, profile_img, gender)" \
                  f"VALUES ({user}, {name}, {profile_image}, {gender})"
            database.execute(sql)
            database.commit()
        else:
            user = row['id']

        return get_token(user)

@oauth.route('/naver')
class NaverLoginAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('code', type=str, required=True)
        parser.add_argument('state', type=str, required=True)
        args = parser.parse_args()

        self.code = args['code']
        self.state = args['state']

    @oauth.expect(model_naver_auth)
    def post(self):
        """Naver 로그인"""
        token_json = get_naver_token(self.state, self.code)
        error = token_json.get("error", None)
        if error is not None:
            return make_response({"message": "INVALID_CLIENT"}, 400)

        access_token = token_json['access_token']
        token_type = token_json['token_type']
        profile = get_naver_profile(access_token, token_type)
        email = profile['email']
        sql1 = f"SELECT * FROM User " \
               f"WHERE platform_type = 'Naver' AND email = {email}"
        row = database.execute_one(sql1)
        if row is None:
            platform_id = profile['id']
            sql2 = f"INSERT INTO User (platform_type, email, platform_id)" \
                   f"VALUES ('Naver', {email}, {platform_id})"
            database.execute(sql2)
            database.commit()

            row = database.execute_one(sql1)
            user = row['id']
            name = profile['name']
            profile_image = profile['profile_image']
            gender = profile['gender']
            sql = f"INSERT INTO Profile (id, name, profile_img, gender)" \
                  f"VALUES ({user}, {name}, {profile_image}, {gender})"
            database.execute(sql)
            database.commit()
        else:
            user = row['id']

        return get_token(user)

@oauth.route('/google')
class GoogleLoginAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('code', type=str, required=True)
        args = parser.parse_args()

        self.code = args['code']

    @oauth.expect(model_google_auth)
    def post(self):
        """Google 로그인"""
        token_json = requests.post(
            url="https://www.googleapis.com/oauth2/v4/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "client_id": config['GOOGLE_API']['CLIENT_ID'],
                "client_secret": config['GOOGLE_API']['CLIENT_SECRET'],
                "redirect_uri": f"http://{host}:{port}/oauth/google",
                "code": self.code,
            },
        ).json()
        error = token_json.get("error", None)
        if error is not None:
            return make_response({"message": "INVALID_CLIENT"}, 400)
        access_token = token_json['access_token']
        user_info = requests.get(
            url="https://www.googleapis.com/userinfo/v2/me",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Bearer {access_token}"
            }
        ).json()
        email = user_info['email']

        sql1 = f"SELECT * FROM User " \
               f"WHERE platform_type = 'Google' AND email = {email}"
        row = database.execute_one(sql1)
        if row is None:
            platform_id = user_info['id']
            sql2 = f"INSERT INTO User (platform_type, email, platform_id)" \
                   f"VALUES ('Google', {email}, {platform_id})"
            database.execute(sql2)
            database.commit()

            row = database.execute_one(sql1)
            user = row['id']
            name = user_info['name']
            sql = f"INSERT INTO Profile (id, name)" \
                  f"VALUES ({user}, {name})"
            database.execute(sql)
            database.commit()
        else:
            user = row['id']

        return get_token(user)

def get_naver_token(state, code):
    token_json = requests.post(
        url="https://nid.naver.com/oauth2.0/token",
        data={
            "grant_type": "authorization_code",
            "client_id": config['NAVER_API']['CLIENT_ID'],
            "client_secret": config['NAVER_API']['CLIENT_SECRET'],
            "state": state,
            "code": code,
        },
    ).json()

    return token_json

def get_naver_profile(access_token, token_type='Bearer'):
    profile_info = requests.get(
        profile_url='https://openapi.naver.com/v1/nid/me',
        headers={
            'Authorization': '{} {}'.format(token_type, access_token)
        }
    ).json()

    return profile_info
