from flask import make_response
from flask_restx import Resource
from util.dto import PlaceDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database

place = PlaceDto.api
_place_by_category = PlaceDto.place_by_category
_place_detail = PlaceDto.place_detail
_place_error = PlaceDto.place_error

@place.route('/recommend')
class RecommendPlaceAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @place.doc(security='apiKey')
    @jwt_required()
    def get(self):
        """홈 탭의 추천 장소 (추가예정)"""
        pass

@place.doc(params={
    'sort': {'description': 'location, popular or taste', 'in': 'query', 'type': 'string'},
    'category': {'description': '배열로 입력 ex) ["ALL"] or ["AT"] or ["AT", "FD", "CE2", "CE3", "AC5"]\n\n'
                                '전체: "ALL",\n\n 관광명소전체: "AT", [공원: "AT1", 야경/풍경: "AT2", 식물원/수목원: "AT3",'
                                ' 시장: "AT4", 동물원: "AT5", 지역축제: "AT6", 유적지: "AT7", 바다: "AT8", 산/계곡: "AT9"],\n\n '
                                '음식점전체: "FD", [한식: "FD1", 중식: "FD2", 분식: "FD3", 돈까스/회/일식: "FD4", '
                                '패스트푸드: "FD5", 아시안/양식: "FD6", 치킨/피자: "FD7", 세계음식: "FD8", 채식: "FD9"]\n\n'
                                '카페전체: "CE", [음료전문: "CE1", 디저트전문: "CE2", 테마카페: "CE3", 보드카페: "CE4", '
                                '애견카페: "CE5", 만화/북카페: "CE6", 룸카페: "CE7"]\n\n'
                                '이색체험전체: "UE", [공방: "UE1", 원데이클래스: "UE2", 사진스튜디오: "UE3", 사주/타로: "UE4", '
                                'VR: "UE5", 방탈출: "UE6", 노래방: "UE7"]\n\n'
                                '액티비티전체: "AC", [게임/오락: "AC1", 온천/스파: "AC2", 레저스포츠: "AC3", 테마파크: "AC4", '
                                '아쿠아리움: "AC5", 낚시: "AC6", 캠핑: "AC7"]\n\n'
                                '문화생활전체: "CT", [영화: "CT1", 전시회: "CT2", 공연: "CT3", 스포츠 경기: "CT4", 미술관: "CT5", '
                                '박물관: "CT6", 쇼핑: "CT7"]',
                 'in': 'query', 'type': 'string'},
    'longitude':
        {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'latitude':
        {'description': 'latitude', 'in': 'query', 'type': 'float'}
})
@place.route('')
@place.response(200, 'Success', _place_by_category)
@place.response(400, 'Bad Request', _place_error)
class PlacesByCategoryAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('sort', type=str, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('latitude', type=float, required=True)
        args = parser.parse_args()

        self.sort = args['sort']
        self.category = args['category']
        self.longitude = args['longitude']
        self.latitude = args['latitude']

    @place.doc(security='apiKey')
    @jwt_required()
    def get(self):
        """카테고리별 장소"""
        database = Database()
        category = self.category[2:-2].replace('", "', "|")
        value = {
            'sort': self.sort,
            'category': category,
            'longitude': self.longitude,
            'latitude': self.latitude
        }
        print(category)
        if self.sort == "taste":
            pass

        else:
            if category == 'ALL':
                sql = """
                        SELECT id, name, address, categories, hashtags,
                        (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                        * cos(radians(Place.longitude) - radians(%(longitude)s))
                        + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                        FROM Place
                        WHERE enabled = 1
                        ORDER BY distance
                        LIMIT 0,30
                """
            else:
                sql = """
                    SELECT id, name, address, categories, hashtags,
                    (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                    * cos(radians(Place.longitude) - radians(%(longitude)s))
                    + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                    FROM Place
                    WHERE enabled = 1
                    AND categories REGEXP %(category)s
                    ORDER BY distance
                    LIMIT 0,30
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
            if self.sort == "location":
                return rows, 200

            elif self.sort == "popular":
                # if category == 'ALL':
                #     sql = """
                #             SELECT Place.id, Place.name, Place.categories, Place.hashtags,
                #             AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num,
                #             (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                #             * cos(radians(Place.longitude) - radians(%(longitude)s))
                #             + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                #             FROM Place JOIN Review
                #             WHERE Place.enabled = 1 AND Review.place_id = Place.id
                #             GROUP BY id
                #             ORDER BY distance <= 3, rating desc, review_num desc
                #             LIMIT 0,30
                #     """
                # else:
                #     sql = """
                #             SELECT Place.id, Place.name, Place.categories, Place.hashtags,
                #             AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num,
                #             (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                #             * cos(radians(Place.longitude) - radians(%(longitude)s))
                #             + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                #             FROM Place JOIN Review
                #             WHERE Place.enabled = 1 AND Review.place_id = Place.id
                #             AND Place.categories REGEXP %(category)s
                #             GROUP BY id
                #             ORDER BY distance <= 3, rating desc, review_num desc
                #             LIMIT 0,30
                #     """
                # rows = database.execute_all(sql, value)

                result = sorted(rows, key=lambda x: str(x['review_rating'])[:3], reverse=False)
                return result, 200

            else:
                return make_response({'message': 'Invalid request.'}, 400)

@place.route('/<int:place_id>')
@place.response(200, 'Success', _place_detail)
@place.response(400, 'Bad Request', _place_error)
class PlaceInfoAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @place.doc(security='apiKey')
    @jwt_required()
    def get(self, place_id):
        """장소 상세정보"""
        database = Database()
        sql = """
            SELECT id, name, address, road_address, categories, hashtags,
            phone, url, longitude, latitude, descriptions
            FROM Place
            WHERE id = %(place_id)s AND enabled = 1
        """
        row = database.execute_one(sql, {'place_id': place_id})

        if row is None:
            return {'message': f'Place id \'{place_id}\' does not exist.'}, 400
        else:
            sql = """
                SELECT * FROM Review 
                WHERE place_id = %(place_id)s
            """
            review_row = database.execute_one(sql, {'place_id': place_id})
            if review_row is None:
                row['review_rating'] = 0
                row['review_num'] = 0

            else:
                sql = """
                    SELECT AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num
                    FROM Review
                    WHERE place_id = %(place_id)s
                """
                review_row = database.execute_one(sql, {'place_id': place_id})
                row['review_rating'] = review_row['rating']
                row['review_num'] = review_row['review_num']
        return row, 200

@place.route('/<int:place_id>/like')
@place.response(200, 'Success')
@place.response(400, 'Bad Request', _place_error)
class PlaceLikeAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        self.user_id = get_jwt_identity()

    @place.doc(security='apiKey')
    def post(self, place_id):
        """장소 좋아요 누르기 또는 취소하기"""
        database = Database()
        sql = f"SELECT id FROM Place WHERE id = {place_id}"
        row = database.execute_one(sql)
        if row is None:
            return {'message': f'Place id \'{place_id}\' does not exist.'}, 400
        else:
            value = {
                'place_id': place_id,
                'user_id': self.user_id
            }
            sql = """
                SELECT id, enabled FROM Place_User
                WHERE place_id = %(place_id)s AND user_id = %(user_id)s
            """
            row = database.execute_one(sql, value)
            if row is None:
                sql = """
                    INSERT INTO Place_User (place_id, user_id) 
                    VALUES (%(place_id)s, %(user_id)s)
                """
            else:
                if row['enabled'] == 1:
                    sql = """
                        UPDATE Place_User SET enabled = 0 
                        WHERE place_id = %(place_id)s AND user_id = %(user_id)s
                    """
                elif row['enabled'] == 0:
                    sql = """
                        UPDATE Place_User SET enabled = 1
                        WHERE place_id = %(place_id)s AND user_id = %(user_id)s
                    """
            database.execute(sql, value)
            database.commit()

            return 200