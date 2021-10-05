from flask_restx import Namespace, fields

class ReviewDto:
    api = Namespace('Review', description='장소 리뷰')
    review = api.model('review', {
        'rating': fields.Float(description='Review rating'),
        'content': fields.String(description='Review content')
    })
    review_detail = api.model('review_detail', {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'place_id': fields.Integer,
        'rating': fields.Float,
        'content': fields.String,
        'created_at': fields.DateTime(example='yyyy-mm-dd hh:mm:ss'),
        'user_name': fields.String,
        'profile_img': fields.String
    })
    review_error = api.model('review_error', {
        'message': fields.String
    })
    review_by_place = api.model('review_by_place', {
        'review_num': fields.Integer,
        'result': fields.List(fields.Nested(review_detail))
    })
