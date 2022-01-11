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
        'profile_img': fields.String(example="http://owncourse.seongbum.com/static/uploads/profileIMG.jpeg"),
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
        'categories': fields.Raw(example=["음료전문", "디저트전문"]),
        'hashtags': fields.Raw(example=["조용한", "데이트"]),
        'review_rating': fields.Float,
        'review_num': fields.Integer,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    user_review_detail = api.model('user_review_detail', {
        'review_id': fields.Integer,
        'place_id': fields.Integer,
        'name': fields.String,
        'rating': fields.Float,
        'content': fields.String,
        'review_img': fields.String(example=["http://owncourse.seongbum.com/static/uploads/reviewIMG.jpeg"]),
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
        'user_name': fields.String,
        'profile_img': fields.String(example="http://owncourse.seongbum.com/static/uploads/profileIMG.jpeg")
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
    place_recommend = api.model('place_recommend', {
        'id': fields.Integer,
        'name': fields.String,
        'categories': fields.Raw(example=["FD1"]),
        'large_categories': fields.Raw(example=["FD"]),
        'like': fields.Boolean,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    place_by_category = api.model('place_by_category', {
        'id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
        'categories': fields.Raw(example=["음료전문"]),
        'hashtags': fields.Raw(example=["조용한", "데이트"]),
        'distance': fields.Float,
        'review_rating': fields.Float,
        'review_num': fields.Integer,
        'like': fields.Boolean,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    place_description = api.model('place_description', {
        'source': fields.String(example="카카오맵"),
        'description': fields.String
    })
    place_detail = api.model('place_detail', {
        'id': fields.Integer,
        'name': fields.String,
        'address': fields.String,
        'road_address': fields.String,
        'categories': fields.Raw(example=["음료전문"]),
        'hashtags': fields.Raw(example=["조용한", "데이트"]),
        'phone': fields.String,
        'longitude': fields.Float,
        'latitude': fields.Float,
        'descriptions': fields.List(fields.Nested(place_description)),
        'review_rating': fields.Float,
        'review_num': fields.Integer,
        'like': fields.Boolean,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    place_like = api.model('place_like', {
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
        'review_img': fields.Raw(example=["http://owncourse.seongbum.com/static/uploads/reviewIMG.jpeg"]),
        'like_num': fields.Integer,
        'source': fields.String,
        'created_at': fields.DateTime(example='yyyy-mm-dd hh:mm:ss'),
        'user_name': fields.String,
        'profile_img': fields.String(example="http://owncourse.seongbum.com/static/uploads/profileIMG.jpeg"),
        'like': fields.Boolean
    })
    review_img_detail = api.model('review_img_detail', {
        'review_id': fields.Integer,
        'rating': fields.Float,
        'review_img': fields.Raw(example=["http://owncourse.seongbum.com/static/uploads/reviewIMG.jpeg"])
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
    review_like = api.model('review_like', {
        'like': fields.Boolean
    })


class CourseDto:
    api = Namespace('Course', description='코스')
    course_id = api.model('course_id', {
        'course_id': fields.Integer
    })
    course_info = api.model('course_info', {
        'place_id': fields.Integer,
        'place_order': fields.Integer
    })
    course_place_description = api.model('course_place_description', {
        'source': fields.String(example="카카오맵"),
        'description': fields.String
    })
    course_recommend = api.model('course_recommend', {
        'id': fields.Integer,
        'name': fields.String,
        'categories': fields.Raw(example=["FD1"]),
        'latitude': fields.Float,
        'longitude': fields.Float,
        'large_categories': fields.Raw(example=["FD"]),
        'avg_price': fields.Integer,
        'representative_menu': fields.String,
        'like': fields.Boolean,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg"),
        'phone': fields.String,
        'hashtags': fields.Raw(example=["조용한", "데이트"]),
        'descriptions': fields.List(fields.Nested(course_place_description)),
        'review_rating': fields.Float(example=4.5),
        'review_num': fields.Integer(example=10)
    })
    course_replacement = api.inherit('course_replacement', course_recommend, {
        'review_rating': fields.Float(example=4.5),
        'review_num': fields.Integer,
        'hashtags': fields.Raw(example=["조용한", "데이트"])
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
        'address': fields.String,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    course_detail = api.model('course_detail', {
        'place_id': fields.Integer,
        'place_order': fields.Integer,
        'avg_cost': fields.Integer,
        'popular_menu': fields.String,
        'name': fields.String,
        'address': fields.String,
        'road_address': fields.String,
        'categories': fields.String(example=["음료전문"]),
        'hashtags': fields.String(example=["조용한", "데이트"]),
        'phone': fields.String,
        'longitude': fields.Float,
        'latitude': fields.Float,
        'descriptions': fields.List(fields.Nested(course_place_description)),
        'like': fields.Boolean,
        'review_rating': fields.Float,
        'review_num': fields.Integer,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    course_error = api.model('course_error', {
        'message': fields.String
    })
