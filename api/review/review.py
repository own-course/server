from flask_restx import Resource
from util.dto import ReviewDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database
import json

review = ReviewDto.api
_review = ReviewDto.review
_review_detail = ReviewDto.review_detail
_review_error = ReviewDto.review_error
_review_by_place = ReviewDto.review_by_place

@review.route('/<int:place_id>')
@review.doc(params={'place_id': 'place ID'})
@review.response(400, 'Bad Request', _review_error)
class PlaceReviewAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('rating', type=float)
        parser.add_argument('content', type=str)
        parser.add_argument('page', type=int)
        args = parser.parse_args()

        self.rating = args['rating']
        self.content = args['content']
        self.page = args['page']
        self.user_id = get_jwt_identity()

    @review.expect(_review)
    @review.doc(security='apiKey')
    @review.response(200, 'Success')
    def post(self, place_id):
        """Review 등록"""
        database = Database()
        sql = """
            SELECT id FROM Place
            WHERE id = %(place_id)s
        """
        row = database.execute_one(sql, {'place_id': place_id})
        if row is None:
            return {'message': f'Place ID \'{place_id}\' does not exist.'}, 400
        else:
            value = {
                'user_id': self.user_id,
                'place_id': place_id,
                'rating': self.rating,
                'content': self.content
            }
            sql = """
                INSERT INTO Review (user_id, place_id, rating, content, source)
                VALUES (%(user_id)s, %(place_id)s,%(rating)s, %(content)s, 'owncourse')
            """
            database.execute(sql, value)
            database.commit()

            return 200

    @review.doc(security='apiKey')
    @review.doc(params={
        'page':
            {'description': 'pagination', 'in': 'query', 'type': 'int'}}
    )
    @review.response(200, 'Success', _review_by_place)
    def get(self, place_id):
        """특정 장소의 Review 가져오기"""
        database = Database()
        sql = """
                SELECT id FROM Place
                WHERE id = %(place_id)s
        """
        row = database.execute_one(sql, {'place_id': place_id})
        if row is None:
            return {'message': f'Place ID \'{place_id}\' does not exist.'}, 400
        else:
            page = self.page - 1
            limit = 10
            value = {
                'place_id': place_id,
                'start': page * limit,
                'limit': limit
            }
            sql = """
                SELECT Review.*, Profile.name AS user_name, Profile.profile_img
                FROM Review JOIN Profile
                WHERE Review.place_id = %(place_id)s AND Review.user_id = Profile.user_id
                ORDER BY Review.created_at desc
                LIMIT %(start)s, %(limit)s 
            """
            rows = database.execute_all(sql, value)
            for row in rows:
                row['created_at'] = json.dumps(row['created_at'].strftime('%Y-%m-%d %H:%M:%S'))
            sql = """
                SELECT COUNT(id) AS review_num FROM Review
                WHERE place_id = %(place_id)s
            """
            row = database.execute_one(sql, {'place_id': place_id})

            return {'review_num': row['review_num'], 'result': rows}, 200

@review.route('/<int:review_id>/detail')
@review.doc(params={'review_id': 'review ID'})
@review.response(200, 'Success', _review_detail)
@review.response(400, 'Bad Request', _review_error)
class ReviewDetailAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @review.doc(security='apiKey')
    def get(self, review_id):
        """리뷰 상세정보"""
        database = Database()
        sql = """
            SELECT Review.*, Profile.name AS user_name, Profile.profile_img
            FROM Review JOIN Profile
            WHERE Review.id = %(review_id)s AND Review.user_id = Profile.user_id
        """
        row = database.execute_one(sql, {'review_id': review_id})
        if row is None:
            return {'message': f'Review ID \'{review_id}\' does not exist.'}, 400
        else:
            row['created_at'] = json.dumps(row['created_at'].strftime('%Y-%m-%d %H:%M:%S'))
            return row, 200

