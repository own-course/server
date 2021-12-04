from flask import make_response
from flask_restx import Resource
from util.dto import CourseDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database
from util.recommend import recommend_poi
import json

course = CourseDto.api
_course = CourseDto.course
_course_recommend = CourseDto.course_recommend
_course_error = CourseDto.course_error
_course_list = CourseDto.course_list
_course_detail = CourseDto.course_detail


@course.doc(params={
    'category':
        {'description': '배열로 입력 ex) ["FD"] or ["FD1","FD2","CE1","AT"]\n\n'
                        '카테고리 대분류 전체를 지칭하는 경우, 하위 카테고리 번호를 쓰지 않고 상위 코드만 입력\n'
                        'ex) 음식점 전체를 선택한 경우: ["FD"], 한식과 중식을 선택한 경우: ["FD1", "FD2"]\n\n'
                        '카테고리 코드: https://aged-dog-e5f.notion.site/d66c00aef41149a09450ae102525c961?v=3262fc0ad0e245e189d6ea67099bf513\n\n',
         'in': 'query', 'type': 'string'},
    'hours': {'description': 'hours in hours (ex) 2', 'in': 'query', 'type': 'float'},
    'distance': {'description': 'distance in meters (ex) 1500', 'in': 'query', 'type': 'int'},
    'cost': {'description': 'cost in won (ex) 30000', 'in': 'query', 'type': 'int'},
    'latitude': {'description': 'latitude', 'in': 'query', 'type': 'float'},
    'longitude': {'description': 'longitude', 'in': 'query', 'type': 'float'}
})
@course.route('/recommend')
@course.response(200, 'Success', [[_course_recommend]])
@course.response(400, 'Bad Request', _course_error)
class RecommendCourseAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('hours', type=float, required=True)
        parser.add_argument('distance', type=int, required=True)
        parser.add_argument('cost', type=int, required=True)
        parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('longitude', type=float, required=True)
        args = parser.parse_args()

        self.user_id = get_jwt_identity()
        self.category = json.loads(args['category'])
        self.hours = args['hours']
        self.distance = args['distance']
        self.cost = args['cost']
        self.latitude = args['latitude']
        self.longitude = args['longitude']

    @course.doc(security='apiKey')
    def get(self):
        """코스 추천 """
        # POI 추천 결과
        rec_poi_list = recommend_poi(self.user_id, self.latitude, self.longitude, self.distance)

        # 카테고리 필터링
        def category_filter(item):
            return (len(set(item['categories']) & set(self.category)) > 0
                or len(set(item['large_categories']) & set(self.category)) > 0)
        poi_list = list(filter(category_filter, rec_poi_list))

        # 사용자 선택 카테고리의 대분류 리스트
        large_categories = [category[:2] for category in self.category]

        # 카테고리 대분류 별 POI
        # 카테고리가 여러 개인 POI는 여러 카테고리의 리스트에 존재할 수 있음
        category_poi = {}
        for category_list in [poi['large_categories'] for poi in poi_list]:
            for category in category_list:
                if category[:2] in large_categories:
                    category_poi[category] = []

        for poi in poi_list:
            for category in poi['large_categories']:
                if category[:2] in large_categories:
                    category_poi[category].append(poi)

        # 코스 구성 (최대 10개)
        courses = []
        course_size = min(min([len(data) for _, data in category_poi.items()]), 10)

        for i in range(0, course_size):
            course = []
            category_set = set()
            
            for category, data in category_poi.items():
                poi = data[i]
                
                if len(set(poi['large_categories']) & category_set) > 0:
                    continue
                
                course.append(poi)
                if len(set(poi['large_categories']) & set(large_categories)) > 0:
                    category_set.update(poi['large_categories'])
            
            # TSC순 정렬
            course = sorted(course, key=lambda poi: poi['tsc_score'], reverse=True)
            
            courses.append(course)

        database = Database()

        for course in courses:
            for item in course:
                value = {
                    'place_id': item['id'],
                    'user_id': self.user_id
                }
                sql = """
                    SELECT AVG(CAST(price as FLOAT)) as avg_price FROM Place_Menu
                    WHERE place_id = %(place_id)s
                """
                row = database.execute_one(sql, value)
                if row['avg_price'] != -1.0 and row['avg_price'] is not None:
                    item['avg_price'] = int(round(row['avg_price'], -3))
                else:
                    item['avg_price'] = 0

                sql = """
                    SELECT menu_name as representative_menu FROM Place_Menu
                    WHERE place_id = %(place_id)s AND representative = 1
                """
                row = database.execute_one(sql, value)
                if row is None:
                    item['representative_menu'] = "정보없음"
                else:
                    item['representative_menu'] = row['representative_menu']

                del item['taste'], item['service'], item['cost'], item['tsc_score']
                del item['distance'], item['latitude'], item['longitude']

                sql = """
                    SELECT enabled FROM Place_User
                    WHERE place_id = %(place_id)s AND user_id = %(user_id)s
                """
                like = database.execute_one(sql, value)
                if like is None:
                    item['like'] = False
                else:
                    if like['enabled'] == 0:
                        item['like'] = False
                    else:
                        item['like'] = True

        return courses, 200


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
