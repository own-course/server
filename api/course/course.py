from flask import make_response
from flask_restx import Resource
from util.dto import CourseDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database

course = CourseDto.api
_course = CourseDto.course
_course_error = CourseDto.course_error
_course_list = CourseDto.course_list
_course_detail = CourseDto.course_detail


@course.doc(params={
    'category':
        {'description': '배열로 입력 ex) ["전체"] or ["관광명소전체"] or ["관광명소전체","음식점전체","디저트전문",'
                                '"공방","전시회"]\n\n'
                                '관광명소: "관광명소전체", "공원", "야경/풍경", "식물원,수목원", "시장", "동물원", "지역축제", '
                                '"유적지", "바다", "산/계곡"\n\n'
                                '음식점: "음식점전체", "한식", "중식", "분식", "일식", "패스트푸드", "아시안,양식", "치킨,피자", '
                                '"세계음식", "채식", "해산물", "간식", "육류,고기", "기타"\n\n'
                                '카페: "카페전체", "음료전문", "디저트전문", "테마카페", "보드카페", "동물카페", "만화/북카페", '
                                '"룸카페"\n\n'
                                '이색체험: "이색체험전체", "공방", "원데이클래스", "사진스튜디오", "사주/타로", "VR", "방탈출", '
                                '"노래방"\n\n'
                                '액티비티: "액티비티전체", "게임/오락", "온천,스파", "레저스포츠", "테마파크", "아쿠아리움", '
                                '"낚시", "캠핑"\n\n'
                                '문화생활: "문화생활전체", "영화", "전시회", "공연", "스포츠경기", "미술관", "박물관", "쇼핑"\n\n',
         'in': 'query', 'type': 'string'},
    'hours': {'description': 'hours in hours (ex) 2', 'in': 'query', 'type': 'float'},
    'distance': {'description': 'distance in meters (ex) 1500', 'in': 'query', 'type': 'int'},
    'cost': {'description': 'cost in won (ex) 30000', 'in': 'query', 'type': 'int'},
    'longitude': {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'latitude': {'description': 'latitude', 'in': 'query', 'type': 'float'}
})
@course.route('/recommend')
@course.response(200, 'Success')
@course.response(400, 'Bad Request', _course_error)
class RecommendCourseAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('hours', type=float, required=True)
        parser.add_argument('distance', type=int, required=True)
        parser.add_argument('cost', type=int, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('latitude', type=float, required=True)
        args = parser.parse_args()

        self.category = args['category']
        self.hours = args['hours']
        self.distance = args['distance']
        self.cost = args['cost']
        self.longitude = args['longitude']
        self.latitude = args['latitude']

    @course.doc(security='apiKey')
    @jwt_required()
    def get(self):
        """코스 추천 (미완성) """
        database = Database()
        category = self.category[2:-2].replace('", "', "|")
        pass


@course.route('')
class SaveCourseAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('course_name', type=str)
        parser.add_argument('place_num', type=int)
        parser.add_argument('cost', type=int)
        parser.add_argument('hours', type=float)
        parser.add_argument('address', type=str)
        parser.add_argument('longitude', type=float)
        parser.add_argument('latitude', type=float)
        parser.add_argument('course_info', type=dict, action='append')
        args = parser.parse_args()

        self.course_name = args['course_name']
        self.place_num = args['place_num']
        self.cost = args['cost']
        self.hours = args['hours']
        self.address = args['address']
        self.longitude = args['longitude']
        self.latitude = args['latitude']
        self.course_info = args['course_info']
        self.user_id = get_jwt_identity()

    @course.response(200, 'Success')
    @course.expect(_course)
    @course.doc(security='apiKey')
    def post(self):
        """코스 저장"""
        database = Database()
        value = {
            'user_id': self.user_id,
            'course_name': self.course_name,
            'place_num': self.place_num,
            'cost': self.cost,
            'hours': self.hours,
            'address': self.address,
            'longitude': self.longitude,
            'latitude': self.latitude
        }
        sql = """
            INSERT INTO Course (user_id, course_name, place_num, cost, hours, address, longitude, latitude)
            VALUES (%(user_id)s, %(course_name)s, %(place_num)s, %(cost)s, %(hours)s,
            %(address)s, %(longitude)s, %(latitude)s)
        """
        database.execute(sql, value)
        database.commit()

        sql = """
            SELECT LAST_INSERT_ID() as id;
        """
        course_id = database.execute_one(sql)
        for course in self.course_info:
            # if course['avg_cost'] is None and course['popular_menu'] is None:
            #     value = {
            #         'course_id': course_id['id'],
            #         'place_id': course['place_id'],
            #         'place_order': course['place_order'],
            #         'avg_cost': course['avg_cost'],
            #     }
            #     sql = """
            #         INSERT INTO Course_Place (course_id, place_id, place_order)
            #         VALUES (%(course_id)s, %(place_id)s, %(place_order)s)
            #     """
            # elif course['avg_cost'] is None:
            #     value = {
            #         'course_id': course_id['id'],
            #         'place_id': course['place_id'],
            #         'place_order': course['place_order'],
            #         'popular_menu': course['popular_menu'],
            #     }
            #     sql = """
            #         INSERT INTO Course_Place (course_id, place_id, place_order, popular_menu)
            #         VALUES (%(course_id)s, %(place_id)s, %(place_order)s, %(popular_menu)s)
            #     """
            # elif course['popular_menu'] is None:
            #     value = {
            #         'course_id': course_id['id'],
            #         'place_id': course['place_id'],
            #         'place_order': course['place_order'],
            #         'avg_cost': course['avg_cost'],
            #     }
            #     sql = """
            #         INSERT INTO Course_Place (course_id, place_id, place_order, avg_cost)
            #         VALUES (%(course_id)s, %(place_id)s, %(place_order)s, %(avg_cost)s)
            #     """
            # else:
            value = {
                'course_id': course_id['id'],
                'place_id': course['place_id'],
                'place_order': course['place_order'],
                'avg_cost': course['avg_cost'],
                'popular_menu': course['popular_menu']
            }
            sql = """
                INSERT INTO Course_Place (course_id, place_id, place_order, avg_cost, popular_menu)
                VALUES (%(course_id)s, %(place_id)s, %(place_order)s, %(avg_cost)s, %(popular_menu)s)
            """
            database.execute(sql, value)
            database.commit()
        database.close()

        return 200


@course.route('/list')
@course.doc(params={
    'sort': {'description': 'location, cost or hour', 'in': 'query', 'type': 'string'},
    'longitude':
        {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'latitude':
        {'description': 'latitude', 'in': 'query', 'type': 'float'},
    'search':
        {'description': 'search by course name or address (검색어 입력시 사용)', 'in': 'query', 'type': 'string'}
})
@course.response(200, 'Success', _course_list)
class GetCourseListAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('sort', type=str)
        parser.add_argument('longitude', type=float)
        parser.add_argument('latitude', type=float)
        parser.add_argument('search', type=str, required=False)
        args = parser.parse_args()

        self.sort = args['sort']
        self.longitude = args['longitude']
        self.latitude = args['latitude']
        self.search = args['search']
        self.user_id = get_jwt_identity()

    @course.doc(security='apiKey')
    def get(self):
        """저장한 내 코스 목록 불러오기"""
        database = Database()
        value = {
            'user_id': self.user_id,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'search': self.search
        }
        if self.sort == 'location':
            if self.search is None:
                sql = """
                    SELECT id, course_name, cost, hours, address,
                    (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Course.latitude))
                    * cos(radians(Course.longitude) - radians(%(longitude)s))
                    + sin(radians(%(latitude)s)) * sin(radians(Course.latitude)))) AS distance
                    FROM Course
                    WHERE user_id = %(user_id)s
                    ORDER BY distance
                """
            else:
                sql = """
                    SELECT id, course_name, cost, hours, address,
                    (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Course.latitude))
                    * cos(radians(Course.longitude) - radians(%(longitude)s))
                    + sin(radians(%(latitude)s)) * sin(radians(Course.latitude)))) AS distance
                    FROM Course
                    WHERE user_id = %(user_id)s AND course_name REGEXP %(search)s OR address REGEXP %(search)s
                    ORDER BY distance
                """
        elif self.sort == 'cost':
            if self.search is None:
                sql = """
                    SELECT id, course_name, cost, hours, address FROM Course
                    WHERE user_id = %(user_id)s ORDER BY cost
                """
            else:
                sql = """
                    SELECT id, course_name, cost, hours, address FROM Course
                    WHERE user_id = %(user_id)s AND course_name REGEXP %(search)s OR address REGEXP %(search)s
                    ORDER BY cost
                """
        elif self.sort == 'hour':
            if self.search is None:
                sql = """
                    SELECT id, course_name, cost, hours, address FROM Course
                    WHERE user_id = %(user_id)s ORDER BY hours
                """
            else:
                sql = """
                    SELECT id, course_name, cost, hours, address FROM Course
                    WHERE user_id = %(user_id)s AND course_name REGEXP %(search)s OR address REGEXP %(search)s
                    ORDER BY hours
                """
        rows = database.execute_all(sql, value)
        database.close()

        return rows, 200


@course.route('/<int:course_id>/detail')
@course.response(200, 'Success', _course_detail)
@course.response(400, 'Bad Request', _course_error)
class SaveCourseDetailAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        self.user_id = get_jwt_identity()

    @course.doc(security='apiKey')
    def get(self, course_id):
        """코스 상세 정보"""
        database = Database()
        value = {
            'course_id': course_id
        }
        sql = """
            SELECT * FROM Course WHERE id = %(course_id)s
        """
        row = database.execute_one(sql, value)
        if row is None:
            database.close()

            return {'message': f'Course id \'{course_id}\' does not exist.'}, 400

        sql = """
            SELECT Course_Place.place_id, Course_Place.place_order, Course_Place.avg_cost, Course_Place.popular_menu,
            Place.name, Place.address, Place.road_address, Place.categories, Place.hashtags,
            Place.phone, Place.longitude, Place.latitude, Place.descriptions
            FROM Course_Place JOIN Place
            WHERE Course_Place.course_id = %(course_id)s AND Course_Place.place_id = Place.id
        """
        rows = database.execute_all(sql, value)

        for row in rows:
            sql = """
                SELECT enabled FROM Place_User
                WHERE place_id = %(place_id)s AND user_id = %(user_id)s
            """
            like = database.execute_one(sql, {'place_id': row['place_id'], 'user_id': self.user_id})
            if like is None:
                row['like'] = False
            else:
                if like['enabled'] == 0:
                    row['like'] = False
                else:
                    row['like'] = True
            sql = """
                SELECT * FROM Review 
                WHERE place_id = %(place_id)s
            """
            review_row = database.execute_one(sql, {'place_id': row['place_id']})
            if review_row is None:
                row['review_rating'] = 0
                row['review_num'] = 0

            else:
                sql = """
                    SELECT AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num
                    FROM Review
                    WHERE place_id = %(place_id)s
                """
                review_row = database.execute_one(sql, {'place_id': row['place_id']})
                row['review_rating'] = review_row['rating']
                row['review_num'] = review_row['review_num']
        database.close()

        return rows, 200
