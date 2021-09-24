from flask import make_response
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database

place = Namespace('Place', description='장소 API')

@place.route('/recommend')
class RecommendPlaceAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @jwt_required(refresh=True)
    def get(self):
        """홈 탭의 추천 장소"""
        pass

@place.doc(params={
    'category': 'taste, location or popular',
    'category_code': 'all, attraction, food, cafe, unique, activity or culture',
    'longitude':
        {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'latitude':
        {'description': 'latitude', 'in': 'query', 'type': 'float'}
})
@place.route('/<string:category>/<string:category_code>')
class PlacesByCategoryAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('latitude', type=float, required=True)
        args = parser.parse_args()

        self.longitude = args['longitude']
        self.latitude = args['latitude']

    @jwt_required(refresh=True)
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
            sql = """
                    SELECT Place.id, Place.name, Place.category_name, Place.hashtags,
                    AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num,
                    (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                    * cos(radians(Place.longitude) - radians(%(longitude)s))
                    + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                    FROM Place JOIN Review
                    WHERE Place.category_code = %(category_code)s AND Place.enabled = 1
                    AND Review.place_id = Place.id
                    ORDER BY distance
                    LIMIT 0,10
            """
            rows = database.execute_all(sql, value)
            return rows, 200

        elif category == "popular":

            sql = """
                    SELECT Place.id, Place.name, Place.category_name, Place.hashtags,
                    AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num,
                    (6371 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude)) 
                    * cos(radians(Place.longitude) - radians(%(longitude)s)) 
                    + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance 
                    FROM Place JOIN Review
                    WHERE Place.category_code = %(category_code)s AND Place.enabled = 1
                    AND Review.place_id = Place.id
                    ORDER BY distance <= 3, review_num, rating
                    LIMIT 0,10
            """
            rows = database.execute_all(sql, value)
            return rows, 200

        else:
            return make_response({'message': 'Invalid request.'}, 400)

@place.route('/<int:place_id>')
class PlaceInfoAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @jwt_required(refresh=True)
    def get(self, place_id):
        """장소 상세정보"""
        database = Database()

        sql = """
            SELECT Place.*, AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num
            FROM Place JOIN Review
            ON Place.enabled = 1 AND Place.id = %(place_id)s AND Review.place_id = Place.id
        """

        row = database.execute_one(sql, {'place_id': place_id})
        if row is None:
            return make_response({'message': 'The place id does not exist.'}, 400)

        return row, 200