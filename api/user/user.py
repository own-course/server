import json
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
_user_review = UserDto.user_review
_user_notification = UserDto.user_notification
_user_TSC = UserDto.user_TSC
_user_TSC_type = UserDto.user_TSC_type


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
    def put(self):
        """회원가입 후 프로필(닉네임) 설정"""
        if self.nickname is None:
            return {'message': 'No data'}, 400
        database = Database()

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
        value = {
            'user_id': self.user_id
        }
        sql = """
            SELECT Profile.user_id, Profile.nickname, Profile.tsc_type, Profile.profile_img,
            User.platform_type, User.email
            FROM Profile JOIN User
            WHERE Profile.user_id = %(user_id)s AND Profile.user_id = User.id
        """
        row = database.execute_one(sql, value)
        sql = """
            SELECT COUNT(id) AS review_num FROM Review
            WHERE user_id = %(user_id)s 
        """
        review_num = database.execute_one(sql, value)
        row['review_num'] = review_num['review_num']
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
    def put(self):
        """프로필 이미지 설정"""
        database = Database()

        result = upload_file(request.files)
        if result['message'] == 'Success':
            profile_img = result['filename']
            value = {
                'user_id': self.user_id,
                'profile_img': profile_img[1:-2]
            }

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
        parser.add_argument('keyword', type=str, action='append')
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
        result = []
        for keyword in self.keyword:
            result.append(keyword)
        if row is None:
            database.close()

            return {'message': 'The user does not exist.'}, 400

        sql = f"UPDATE Profile SET keyword = \"{result}\" " \
              f"WHERE user_id = {self.user_id}"
        database.execute(sql)
        database.commit()
        database.close()

        return 200


@user.route('/place')
@user.response(200, 'Success', _liked_places)
@user.response(400, 'Bad Request', _user_error)
@user.doc(params={
    'page':
        {'description': 'pagination (start=1) 10개씩 반환', 'in': 'query', 'type': 'int'}}
)
class GetLikedPlaceAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('page', type=int, required=True)
        args = parser.parse_args()

        self.page = args['page']
        self.user_id = get_jwt_identity()

    @user.doc(security='apiKey')
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


@user.route('/review')
@user.response(200, 'Success', _user_review)
@user.response(400, 'Bad Request', _user_error)
@user.doc(params={
    'page':
        {'description': 'pagination (start=1) 10개씩 반환', 'in': 'query', 'type': 'int'},
    'sort':
        {'description': 'location, hour or popular', 'in': 'query', 'type': 'string'},
    'longitude':
        {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'latitude':
        {'description': 'latitude', 'in': 'query', 'type': 'float'}
})
class GetReviewAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('page', type=int, required=True)
        parser.add_argument('sort', type=str, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('latitude', type=float, required=True)
        args = parser.parse_args()

        self.page = args['page']
        self.sort = args['sort']
        self.longitude = args['longitude']
        self.latitude = args['latitude']
        self.user_id = get_jwt_identity()

    @user.doc(security='apiKey')
    def get(self):
        """내가 작성한 리뷰 불러오기"""
        database = Database()
        page = self.page - 1
        limit = 10
        value = {
            'user_id': self.user_id,
            'sort': self.sort,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'start': page * limit,
            'limit': limit
        }

        if self.sort == 'location':
            sql = """
                SELECT Review.id AS review_id, Place.id AS place_id, Place.name, Review.rating, Review.content,
                Review.review_img, Review.likes, Review.source, Review.created_at, 
                (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                * cos(radians(Place.longitude) - radians(%(longitude)s))
                + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                FROM Place JOIN Review
                WHERE Review.user_id = %(user_id)s AND Review.place_id = Place.id
                ORDER BY distance
                LIMIT %(start)s, %(limit)s
            """
        elif self.sort == 'hour':
            sql = """
                SELECT Review.id AS review_id, Place.id AS place_id, Place.name, Review.rating, Review.content, 
                Review.review_img, Review.likes, Review.source, Review.created_at,
                (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                * cos(radians(Place.longitude) - radians(%(longitude)s))
                + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                FROM Place JOIN Review
                WHERE Review.user_id = %(user_id)s AND Review.place_id = Place.id
                ORDER BY created_at desc
                LIMIT %(start)s, %(limit)s
            """
        elif self.sort == 'popular':
            sql = """
                SELECT Review.id AS review_id, Place.id AS place_id, Place.name, Review.rating, Review.content, 
                Review.review_img, Review.likes, Review.source, Review.created_at,
                (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                * cos(radians(Place.longitude) - radians(%(longitude)s))
                + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                FROM Place JOIN Review
                WHERE Review.user_id = %(user_id)s AND Review.place_id = Place.id
                ORDER BY likes desc, created_at desc
                LIMIT %(start)s, %(limit)s
            """
        rows = database.execute_all(sql, value)
        for row in rows:
            if row['review_img'] is not None:
                row['review_img'] = row['review_img'].split('"')[1]
            row['created_at'] = json.dumps(row['created_at'].strftime('%Y-%m-%d %H:%M:%S'))
        sql = """
            SELECT COUNT(id) AS review_num FROM Review
            WHERE user_id = %(user_id)s
        """
        row = database.execute_one(sql, {'user_id': self.user_id})

        database.close()

        return {'review_num': row['review_num'], 'result': rows}, 200


@user.route('/notification')
@user.response(200, 'Success', _user_notification)
class GetNotificationAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        self.user_id = get_jwt_identity()

    @user.doc(security='apiKey')
    def get(self):
        """알림"""
        database = Database()
        sql = """
            SELECT Review_User.review_id, Review_User.user_id, Review_User.updated_at as created_at
            FROM Review_User JOIN Review
            WHERE Review.user_id = %(user_id)s AND Review.id = Review_User.review_id AND Review_User.enabled = 1
            ORDER BY created_at desc
        """
        rows = database.execute_all(sql, {'user_id': self.user_id})
        for row in rows:
            sql = """
                SELECT nickname FROM Profile
                WHERE user_id = %(user_id)s
            """
            user = database.execute_one(sql, {'user_id': row['user_id']})
            row['user_name'] = user['nickname']
            row['created_at'] = json.dumps(row['created_at'].strftime('%Y-%m-%d %H:%M:%S'))

        database.close()

        return rows, 200


@user.route('/TSC')
@user.response(200, 'Success', _user_TSC_type)
class TSCTestAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('TSC_answer', type=str)
        args = parser.parse_args()

        self.TSC_answer = args['TSC_answer']
        self.user_id = get_jwt_identity()

    @user.expect(_user_TSC)
    @user.doc(security='apiKey')
    def put(self):
        """TSC 테스트"""
        answer = self.TSC_answer
        T = 0
        S = 0
        C = 0
        for i in range(0, 3):
            result = TSCScore(answer[i])
            S += result[0]
            T += result[1]
        for i in range(3, 4):
            result = TSCScore(answer[i])
            T += result[0]
            S += result[1]
        for i in range(4, 6):
            result = TSCScore(answer[i])
            S += result[0]
            C += result[1]
        for i in range(6, 8):
            result = TSCScore(answer[i])
            C += result[0]
            S += result[1]
        for i in range(8, 9):
            result = TSCScore(answer[i])
            T += result[0]
            C += result[1]
        for i in range(9, 12):
            result = TSCScore(answer[i])
            C += result[0]
            T += result[1]
        type = myTSCType(T, S, C)

        database = Database()
        value = {
            'T': round(T / 1.2, 3),
            'S': round(S / 1.2, 3),
            'C': round(C / 1.2, 3),
            'tsc_type': type,
            'user_id': self.user_id
        }
        sql = """
            UPDATE Profile SET t = %(T)s, s = %(S)s, c = %(C)s, tsc_type = %(tsc_type)s
            WHERE user_id = %(user_id)s
        """
        database.execute(sql, value)
        database.commit()
        database.close()

        return {'TSC_type': type}, 200


def TSCScore(answer):
    if answer == "1":
        return [10, 0]
    elif answer == "2":
        return [7.5, 2.5]
    elif answer == "3":
        return [5, 5]
    elif answer == "4":
        return [2.5, 7.5]
    elif answer == "5":
        return [0, 10]


def myTSCType(T, S, C):
    TSC = [['T', T], ['S', S], ['C', C]]
    TSC.sort(key=lambda x: x[1], reverse=True)
    type = TSC[0][0] + TSC[1][0] + TSC[2][0]

    return type
