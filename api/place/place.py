from flask import make_response
from flask_restx import Resource
from util.dto import PlaceDto
from flask_jwt_extended import jwt_required
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
    'category': '거리순: location (취향순, 인기순 추가예정)',
    'category_code': '전체: ALL, 관광명소: AT, 음식점: FD, 카페: CE, 이색체험: UE, 액티비티: AC, 문화생활: CT',
    'longitude':
        {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'latitude':
        {'description': 'latitude', 'in': 'query', 'type': 'float'}
})
@place.route('/<string:category>/<string:category_code>')
@place.response(200, 'Success', _place_by_category)
@place.response(400, 'Bad Request', _place_error)
class PlacesByCategoryAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('latitude', type=float, required=True)
        args = parser.parse_args()

        self.longitude = args['longitude']
        self.latitude = args['latitude']

    @place.doc(security='apiKey')
    @jwt_required()
    def get(self, category, category_code):
        """카테고리별 장소"""
        database = Database()
        value = {
            'category_code': category_code,
            'longitude': self.longitude,
            'latitude': self.latitude
        }

        if category == "taste":
            pass

        elif category == "location":
            if category_code == 'ALL':
                sql = """
                        SELECT id, name, address, categories, hashtags,
                        (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                        * cos(radians(Place.longitude) - radians(%(longitude)s))
                        + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                        FROM Place
                        WHERE enabled = 1
                        ORDER BY distance
                        LIMIT 0,10
                """
            else:
                sql = """
                    SELECT id, name, address, categories, hashtags,
                    (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                    * cos(radians(Place.longitude) - radians(%(longitude)s))
                    + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                    FROM Place
                    WHERE enabled = 1
                    AND categories REGEXP %(category_code)s
                    ORDER BY distance
                    LIMIT 0,10
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

            return rows, 200

        elif category == "popular":
            sql = """
                    SELECT Place.id, Place.name, Place.categories, Place.hashtags,
                    AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num,
                    (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude)) 
                    * cos(radians(Place.longitude) - radians(%(longitude)s)) 
                    + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance 
                    FROM Place JOIN Review
                    WHERE Place.categories = %(category_code)s AND Place.enabled = 1
                    AND Review.place_id = Place.id
                    GROUP BY id
                    ORDER BY distance <= 3, review_num, rating
                    LIMIT 0,10
            """
            rows = database.execute_all(sql, value)

            return rows, 200

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