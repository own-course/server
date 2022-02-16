from flask_restx import Resource
from util.dto import CourseDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database
from util.recommend import recommend_poi
import json
from util.utils import codeToCategory, hashtagToArray, descriptionToArray, imgSelect, isLikedPlace, reviewRatingAndNum, \
    isExistHashtag, isExistDescription, getAvgPrice, getRepresentativeMenu

course = CourseDto.api
_course_id = CourseDto.course_id
_course = CourseDto.course
_course_recommend = CourseDto.course_recommend
_course_replacement = CourseDto.course_replacement
_course_error = CourseDto.course_error
_course_list = CourseDto.course_list
_course_detail = CourseDto.course_detail


@course.doc(params={
    'category':
        {'description': '배열로 입력 ex) ["FD"] or ["FD1","FD2","CE1","AT"]\n\n'
                        '카테고리 대분류 전체를 지칭하는 경우, 하위 카테고리 번호를 쓰지 않고 상위 코드만 입력\n'
                        'ex) 음식점 전체를 선택한 경우: ["FD"], 한식과 중식을 선택한 경우: ["FD1", "FD2"]\n\n'
                        '카테고리 코드: https://aged-dog-e5f.notion.site/d66c00aef41149a09450ae102525c961?v=3262fc0ad0e245e189d6ea67099bf513\n\n',
         'in': 'query', 'type': 'raw'},
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

                getAvgPrice(item, item['id'], database)
                getRepresentativeMenu(item, item['id'], database)

                del item['taste'], item['service'], item['cost'], item['tsc_score'], item['distance']

                isLikedPlace(item, value['place_id'], value['user_id'], database)

                item['img_url'] = imgSelect(item['categories'])

                sql = """
                    SELECT hashtags, phone, descriptions FROM Place
                    WHERE id = %(place_id)s
                """
                row = database.execute_one(sql, value)
                if row['phone'] is not None:
                    item['phone'] = row['phone']
                else:
                    item['phone'] = ""

                isExistHashtag(row)
                item['hashtags'] = row['hashtags']

                isExistDescription(row)
                item['descriptions'] = row['descriptions']

                reviewRatingAndNum(row, value['place_id'], database)
                item['review_rating'] = row['review_rating']
                item['review_num'] = row['review_num']

        database.close()

        return courses, 200


@course.doc(params={
    'category':
        {'description': '배열로 입력 ex) ["FD"] or ["FD1","FD2","CE1","AT"]\n\n'
                        '카테고리 대분류 전체를 지칭하는 경우, 하위 카테고리 번호를 쓰지 않고 상위 코드만 입력\n'
                        'ex) 음식점 전체를 선택한 경우: ["FD"], 한식과 중식을 선택한 경우: ["FD1", "FD2"]\n\n'
                        '카테고리 코드: https://aged-dog-e5f.notion.site/d66c00aef41149a09450ae102525c961?v=3262fc0ad0e245e189d6ea67099bf513\n\n',
         'in': 'query', 'type': 'raw'},
    'hours': {'description': 'hours in hours (ex) 2', 'in': 'query', 'type': 'float'},
    'distance': {'description': 'distance in meters (ex) 1500', 'in': 'query', 'type': 'int'},
    'cost': {'description': 'cost in won (ex) 30000', 'in': 'query', 'type': 'int'},
    'latitude': {'description': 'latitude', 'in': 'query', 'type': 'float'},
    'longitude': {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'place_id': {'description': 'ID of the place to replace', 'in': 'query', 'type': 'int'}
})
@course.route('/recommend/replacement')
@course.response(200, 'Success', [_course_replacement])
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
        parser.add_argument('place_id', type=int, required=True)
        args = parser.parse_args()

        self.user_id = get_jwt_identity()
        self.category = json.loads(args['category'])
        self.hours = args['hours']
        self.distance = args['distance']
        self.cost = args['cost']
        self.latitude = args['latitude']
        self.longitude = args['longitude']
        self.place_id = args['place_id']

    @course.doc(security='apiKey')
    def get(self):
        """코스 생성 중 장소 변경 시 대체 할 장소 추천"""
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

        database = Database()
        sql = """
            SELECT categories FROM Place WHERE id = %(place_id)s
        """
        row = database.execute_one(sql, {'place_id': self.place_id})
        large_category = row['categories'][2:4]
        places = []
        for i in range(10, 20):
            places.append(category_poi[large_category][i])

        for place in places:
            place['img_url'] = imgSelect(place['categories'])
            value = {
                'place_id': place['id'],
                'user_id': self.user_id
            }

            getAvgPrice(place, place['id'], database)
            getRepresentativeMenu(place, place['id'], database)

            del place['taste'], place['service'], place['cost'], place['tsc_score'], place['distance']

            isLikedPlace(place, value['place_id'], value['user_id'], database)
            reviewRatingAndNum(place, value['place_id'], database)

            sql = """
                SELECT hashtags FROM Place WHERE id = %(place_id)s
            """
            row = database.execute_one(sql, value)
            isExistHashtag(row)
            place['hashtags'] = row['hashtags']

        database.close()

        return places, 200


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

    @course.response(200, 'Success', _course_id)
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
            value = {
                'course_id': course_id['id'],
                'place_id': course['place_id'],
                'place_order': course['place_order'],
                'user_id': self.user_id
            }
            getAvgPrice(course, course['place_id'], database)
            getRepresentativeMenu(course, course['place_id'], database)
            value['avg_cost'] = course['avg_price']
            value['representative_menu'] = course['representative_menu']

            sql = """
                INSERT INTO Course_Place (course_id, place_id, place_order, avg_cost, popular_menu)
                VALUES (%(course_id)s, %(place_id)s, %(place_order)s, %(avg_cost)s, %(representative_menu)s)
            """
            database.execute(sql, value)
            database.commit()
        database.close()

        return {'course_id': course_id['id']}, 200


@course.route('/list')
@course.doc(params={
    'sort': {'description': 'location, cost or hour', 'in': 'query', 'type': 'string'},
    'latitude':
        {'description': 'latitude', 'in': 'query', 'type': 'float'},
    'longitude':
        {'description': 'longitude', 'in': 'query', 'type': 'float'},
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
                    (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Course.latitude))
                    * cos(radians(Course.longitude) - radians(%(longitude)s))
                    + sin(radians(%(latitude)s)) * sin(radians(Course.latitude)))) AS distance
                    FROM Course
                    WHERE user_id = %(user_id)s
                    ORDER BY distance
                """
            else:
                sql = """
                    SELECT id, course_name, cost, hours, address,
                    (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Course.latitude))
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
        for row in rows:
            row['img_url'] = imgSelect(["AT"])
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
            isLikedPlace(row, row['place_id'], self.user_id, database)
            reviewRatingAndNum(row, row['place_id'], database)

            row['img_url'] = imgSelect(row['categories'])
            categories = codeToCategory(row['categories'])
            row['categories'] = categories

            isExistHashtag(row)
            isExistDescription(row)

        database.close()

        return rows, 200


@course.route('/recommend/home')
@course.response(200, 'Success', [_course_list])
@course.doc(params={
    'latitude': {'description': 'latitude', 'in': 'query', 'type': 'float'},
    'longitude': {'description': 'longitude', 'in': 'query', 'type': 'float'}
})
class CourseRecommendHomeAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('longitude', type=float)
        parser.add_argument('latitude', type=float)
        args = parser.parse_args()

        self.longitude = args['longitude']
        self.latitude = args['latitude']
        self.user_id = get_jwt_identity()

    @course.doc(security='apiKey')
    def get(self):
        """홈 탭의 추천 코스"""
        database = Database()
        sql = """
            SELECT tsc_type FROM Profile
            WHERE user_id = %(user_id)s
        """
        row = database.execute_one(sql, {'user_id': self.user_id})
        value = {
            'user_id': self.user_id,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'tsc_type': row['tsc_type']
        }
        sql = """
            SELECT 
                c.id, c.course_name, c.cost, c.hours, c.address,
                (6371000*acos(cos(radians(%(latitude)s))*cos(radians(c.latitude))*cos(radians(c.longitude)
                - radians(%(longitude)s)) + sin(radians(%(latitude)s))*sin(radians(c.latitude)))) AS distance
            FROM 
                Course c, Profile p 
            WHERE 
                c.user_id != %(user_id)s AND p.user_id != %(user_id)s 
                AND p.tsc_type = %(tsc_type)s AND p.user_id = c.user_id
            ORDER BY distance
            LIMIT 0, 10
        """
        rows = database.execute_all(sql, value)
        if len(rows) < 10:
            value = {
                'user_id': self.user_id,
                'longitude': self.longitude,
                'latitude': self.latitude,
                'tsc_type': row['tsc_type'],
                'course_num': 10 - len(rows)
            }
            sql = """
                 SELECT 
                    c.id, c.course_name, c.cost, c.hours, c.address,
                    (6371000*acos(cos(radians(%(latitude)s))*cos(radians(c.latitude))*cos(radians(c.longitude)
                    - radians(%(longitude)s)) + sin(radians(%(latitude)s))*sin(radians(c.latitude)))) AS distance
                FROM 
                    Course c, Profile p
                WHERE 
                    p.tsc_type != %(tsc_type)s AND p.user_id = c.user_id 
                    AND c.user_id != %(user_id)s AND p.user_id != %(user_id)s
                ORDER BY distance
                LIMIT 0, %(course_num)s
            """
            add_rows = database.execute_all(sql, value)
            if len(rows) == 0:
                rows = add_rows
            else:
                for i in range(0, len(add_rows)):
                    rows.append(add_rows[i])
        for item in rows:
            del item['distance']
            item['img_url'] = imgSelect(["AT"])

        database.close()

        return rows, 200

