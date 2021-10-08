from flask import request
from flask_restx import Resource
from util.dto import UserDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database
from util.upload import upload_file

user = UserDto.api
_profile = UserDto.profile
_user_profile_error = UserDto.user_profile_error

@user.route('/profile')
class SetProfileAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('nickname', type=str)
        args = parser.parse_args()

        self.nickname = args['nickname']
        self.user_id = get_jwt_identity()

    @user.expect(_profile)
    @user.doc(security='apiKey')
    @user.response(200, 'Success')
    @user.response(400, 'Bad Request', _user_profile_error)
    def post(self):
        """회원가입 후 프로필(닉네임) 설정"""
        if self.nickname is None:
            return {'message': 'No data'}, 400
        database = Database()

        sql = f"SELECT * FROM Profile WHERE user_id = {self.user_id}"
        row = database.execute_one(sql)
        if row is None:
            sql = f"INSERT INTO Profile (user_id, nickname)" \
                  f"VALUES ({self.user_id}, '{self.nickname}')"
            database.execute(sql)
            database.commit()
        else:
            sql = f"UPDATE Profile SET nickname = '{self.nickname}'" \
                  f"WHERE user_id = {self.user_id}"
            database.execute(sql)
            database.commit()

        return 200

@user.route('/profile/img')
class SetProfileImgAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        self.user_id = get_jwt_identity()

    @user.doc(security='apiKey')
    @user.response(200, 'Success')
    @user.response(400, 'Bad Request', _user_profile_error)
    def post(self):
        """프로필 이미지 설정"""
        database = Database()

        result = upload_file(request.files)
        if result['message'] == 'Success':
            profile_img = result['filename']
            value = {
                'user_id': self.user_id,
                'profile_img': profile_img[1:-2]
            }
            sql = f"SELECT * FROM Profile WHERE user_id = {self.user_id}"
            row = database.execute_one(sql)
            if row is None:
                sql = """
                    INSERT INTO Profile (user_id, profile_img)
                    VALUES (%(user_id)s, %(profile_img)s)
                """
                database.execute(sql, value)
                database.commit()
            else:
                sql = """
                    UPDATE Profile SET profile_img = %(profile_img)s
                    WHERE user_id = %(user_id)s
                """
                database.execute(sql, value)
                database.commit()
        else:
            return {'message': result['message']}, 400

        return 200

