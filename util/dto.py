from flask_restx import Namespace, fields

class UserDto:
    api = Namespace('User', description='사용자 API')
    profile = api.model('profile', {
        'nickname': fields.String
    })
    liked_places = api.model('liked_places', {
        'id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
        'categories': fields.String(example='["AT1","AT2"]'),
        'hashtags': fields.String(example='["조용한","데이트"]'),
        'review_rating': fields.Float,
        'review_num': fields.Integer
    })
    user_error = api.model('use_error', {
        'message': fields.String
    })

class PlaceDto:
    api = Namespace('Place', description='장소 API')
    place_by_category = api.model('place_by_category', {
        'id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
        'categories': fields.String(example='["AT1","AT2"]'),
        'hashtags': fields.String(example='["조용한","데이트"]'),
        'distance': fields.Float,
        'review_rating': fields.Float,
        'review_num': fields.Integer
    })
    place_detail = api.model('place_detail', {
        'id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
        'road_address': fields.String,
        'categories': fields.String(example='["AT1","AT2"]'),
        'hashtags': fields.String(example='["조용한","데이트"]'),
        'phone': fields.String,
        'url': fields.String,
        'longitude': fields.Float,
        'latitude': fields.Float,
        'descriptions': fields.String,
        'review_rating': fields.Float,
        'review_num': fields.Integer
    })
    place_error = api.model('place_error', {
        'message': fields.String
    })

class ReviewDto:
    api = Namespace('Review', description='장소 리뷰')
    review = api.model('review', {
        'rating': fields.Float(description='Review rating'),
        'content': fields.String(description='Review content')
    })
    review_id = api.model('review_id', {
        'id': fields.Integer
    })
    review_detail = api.model('review_detail', {
        'id': fields.Integer,
        'user_id': fields.Integer,
        'place_id': fields.Integer,
        'rating': fields.Float,
        'content': fields.String,
        'review_img': fields.String,
        'likes': fields.Integer,
        'source': fields.String,
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

class CourseDto:
    api = Namespace('Course', description='코스')
    course_info = api.model('course_info', {
        'place_id': fields.Integer,
        'place_order': fields.Integer,
        'avg_cost': fields.Integer,
        'popular_menu': fields.String
    })
    course = api.model('course', {
        'course_name': fields.String,
        'place_num': fields.Integer,
        'cost': fields.Integer,
        'hours': fields.Float,
        'address': fields.String,
        'longitude': fields.Float,
        'latitude': fields.Float,
        'course_info': fields.List(fields.Nested(course_info), action='append', description='장소 개수 만큼 입력')
    })
    course_list = api.model('course_list', {
        'id': fields.Integer,
        'course_name': fields.String,
        'cost': fields.Integer,
        'hours': fields.Float,
        'address': fields.String
    })
    course_error = api.model('course_error', {
        'message': fields.String
    })