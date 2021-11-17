from flask import request
from flask_restx import Resource
from util.dto import UserDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database
from util.upload import upload_file

user = UserDto.api
_profile = UserDto.profile
_keyword = UserDto.keyword
_user_error = UserDto.user_error
_liked_places = UserDto.liked_places
_profile_info = UserDto.profile_info

@user.route('/profile')
class ProfileAPI(Resource):
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
    @user.response(400, 'Bad Request', _user_error)
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
        database.close()

        return 200

    @user.doc(security='apiKey')
    @user.response(200, 'Success', _profile_info)
    @user.response(400, 'Bad Request', _user_error)
    def get(self):
        """프로필 정보"""
        database = Database()

        sql = """
            SELECT Profile.user_id, Profile.nickname, Profile.profile_img,
            User.platform_type, User.email
            FROM Profile JOIN User
            WHERE Profile.user_id = %(user_id)s AND Profile.user_id = User.id
        """
        row = database.execute_one(sql, {'user_id': self.user_id})
        database.close()

        return row, 200

@user.route('/profile/img')
class SetProfileImgAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        self.user_id = get_jwt_identity()

    @user.doc(security='apiKey')
    @user.response(200, 'Success')
    @user.response(400, 'Bad Request', _user_error)
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
            database.close()

            return {'message': result['message']}, 400
        database.close()

        return 200

@user.route('/profile/keyword')
class SetKeywordAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('keyword', type=str)
        args = parser.parse_args()

        self.keyword = args['keyword']
        self.user_id = get_jwt_identity()

    @user.expect(_keyword)
    @user.doc(security='apiKey')
    @user.response(200, 'Success')
    @user.response(400, 'Bad Request', _user_error)
    def put(self):
        """분위기 키워드 입력"""
        database = Database()
        sql = f"SELECT * FROM Profile WHERE user_id = {self.user_id}"
        row = database.execute_one(sql)
        if row is None:
            database.close()

            return {'message': 'The user does not exist.'}, 400

        sql = f"UPDATE Profile SET keyword = '{self.keyword}'" \
              f"WHERE user_id = {self.user_id}"
        database.execute(sql)
        database.commit()
        database.close()

        return 200

@user.route('/place')
@user.response(200, 'Success', _liked_places)
@user.response(400, 'Bad Request', _user_error)
class GetLikedPlaceAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('page', type=int)
        args = parser.parse_args()

        self.page = args['page']
        self.user_id = get_jwt_identity()

    @user.doc(security='apiKey')
    @user.doc(params={
        'page':
            {'description': 'pagination (start=1)', 'in': 'query', 'type': 'int'}}
    )
    def get(self):
        """좋아요 누른 장소 불러오기"""
        database = Database()
        page = self.page - 1
        limit = 10
        value = {
            'user_id': self.user_id,
            'start': page * limit,
            'limit': limit
        }
        sql = """
            SELECT Place.id, Place.name, Place.address, Place.categories, Place.hashtags
            FROM Place_User JOIN Place
            WHERE Place_User.place_id = Place.id AND Place_User.user_id = %(user_id)s AND Place_User.enabled = 1
            ORDER BY Place_User.updated_at desc
            LIMIT %(start)s, %(limit)s 
        """
        rows = database.execute_all(sql, value)
        for row in rows:
            sql = """
                SELECT AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num
                FROM Review
                WHERE place_id = %(place_id)s      
            """
            review = database.execute_one(sql, {'place_id': row['id']})
            if review is None:
                row['review_rating'] = 0
                row['review_num'] = 0
            row['review_rating'] = review['rating']
            row['review_num'] = review['review_num']
        database.close()

        return rows, 200
