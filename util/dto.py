from flask_restx import Namespace, fields


class UserDto:
    api = Namespace('User', description='사용자 API')
    profile = api.model('profile', {
        'nickname': fields.String
    })
    profile_info = api.model('profile_info', {
        'user_id': fields.Integer,
        'nickname': fields.String,
        'tsc_type': fields.String,
        'profile_img': fields.String,
        'platform_type': fields.String(example='Email'),
        'email': fields.String,
        'review_num': fields.Integer
    })
    keyword = api.model('keyword', {
        'keyword': fields.Raw(example=["세련", "독특"])
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
    user_review_detail = api.model('user_review_detail', {
        'review_id': fields.Integer,
        'place_id': fields.Integer,
        'name': fields.String,
        'rating': fields.Float,
        'content': fields.String,
        'review_img': fields.String,
        'likes': fields.Integer,
        'source': fields.String(example='owncourse'),
        'created_at': fields.DateTime(example='yyyy-mm-dd hh:mm:ss'),
        'distance': fields.Float
    })
    user_review = api.model('user_review', {
        'review_num': fields.Integer,
        'result': fields.List(fields.Nested(user_review_detail))
    })
    user_notification = api.model('user_notification', {
        'review_id': fields.Integer,
        'user_id': fields.Integer,
        'created_at': fields.DateTime(example='yyyy-mm-dd hh:mm:ss'),
        'user_name': fields.String
    })
    user_TSC = api.model('user_TSC', {
        'TSC_answer': fields.String(example='123241534253')
    })
    user_TSC_type = api.model('user_TSC_type', {
        'TSC_type': fields.String
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
        'categories': fields.String(example='["음료전문","테마카페"]'),
        'hashtags': fields.String(example='["조용한","데이트"]'),
        'distance': fields.Float,
        'review_rating': fields.Float,
        'review_num': fields.Integer,
        'like': fields.Boolean
    })
    place_detail = api.model('place_detail', {
        'id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
        'road_address': fields.String,
        'hashtags': fields.String(example='["조용한","데이트"]'),
        'phone': fields.String,
        'url': fields.String,
        'longitude': fields.Float,
        'latitude': fields.Float,
        'descriptions': fields.String,
        'review_rating': fields.Float,
        'review_num': fields.Integer,
        'like': fields.Boolean
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
        'like_num': fields.Integer,
        'source': fields.String,
        'created_at': fields.DateTime(example='yyyy-mm-dd hh:mm:ss'),
        'user_name': fields.String,
        'profile_img': fields.String,
        'like': fields.Boolean
    })
    review_img_detail = api.model('review_img_detail', {
        'review_id': fields.Integer,
        'rating': fields.Float,
        'review_img': fields.String
    })
    review_error = api.model('review_error', {
        'message': fields.String
    })
    review_by_place = api.model('review_by_place', {
        'review_num': fields.Integer,
        'result': fields.List(fields.Nested(review_detail))
    })
    review_img = api.model('review_img', {
        'review_num': fields.Integer,
        'review_img_num': fields.Integer,
        'result': fields.List(fields.Nested(review_img_detail))
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
    course_detail = api.model('course_detail', {
        'place_id': fields.Integer,
        'place_order': fields.Integer,
        'avg_cost': fields.Integer,
        'popular_menu': fields.String,
        'name': fields.String,
        'address': fields.String,
        'road_address': fields.String,
        'categories': fields.String(example='["AT1","AT2"]'),
        'hashtags': fields.String(example='["조용한","데이트"]'),
        'phone': fields.String,
        'longitude': fields.Float,
        'latitude': fields.Float,
        'descriptions': fields.String,
        'like': fields.Boolean,
        'review_rating': fields.Float,
        'review_num': fields.Integer
    })
    course_error = api.model('course_error', {
        'message': fields.String
    })
