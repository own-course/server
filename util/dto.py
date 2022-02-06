from flask_restx import Namespace, fields


class AuthDto:
    api = Namespace('Auth', description='이메일 회원가입 및 로그인')
    model_auth_email = api.model('model_auth_email', {
        'email': fields.String(description='Email'),
    })
    model_email = api.model('model_email', {
        'email': fields.String(description='Email'),
        'password': fields.String(description='비밀번호')
    })
    auth_email_response = api.model('auth_email_response', {
        'message': fields.String
    })
    auth_email_response_with_code = api.inherit('auth_email_response_with_code', auth_email_response, {
        'code': fields.Integer(example=123456)
    })
    auth_response_with_token = api.model('auth_response_with_token', {
        'access_token': fields.String
    })
    auth_response_with_refresh_token = api.inherit('auth_response_with_refresh_token', auth_response_with_token, {
        'refresh_token': fields.String
    })


class OauthDto:
    api = Namespace('OAuth', description='카카오, 네이버, 구글 로그인')

    model_kakao_auth = api.model('model_kakao_auth', {
        'code': fields.String(description='Kakao authorization code')
    })
    model_naver_auth = api.model('model_naver_auth', {
        'code': fields.String(description='Naver authorization code'),
        'state': fields.String(description='Naver state')
    })
    model_google_auth = api.model('model_google_auth', {
        'code': fields.String(description='Google authorization code')
    })


class UserDto:
    api = Namespace('User', description='사용자 API')
    profile = api.model('profile', {
        'nickname': fields.String
    })
    profile_info = api.model('profile_info', {
        'user_id': fields.Integer(example=1),
        'nickname': fields.String,
        'tsc_type': fields.String,
        'profile_img': fields.String(example="http://owncourse.seongbum.com/static/uploads/profileIMG.jpeg"),
        'platform_type': fields.String(example='Email'),
        'email': fields.String,
        'review_num': fields.Integer(example=1)
    })
    keyword = api.model('keyword', {
        'keyword': fields.Raw(example=["세련", "독특"])
    })
    liked_places = api.model('liked_places', {
        'id': fields.Integer(example=1),
        'name': fields.String,
        'address': fields.String,
        'categories': fields.Raw(example=["음료전문", "디저트전문"]),
        'hashtags': fields.Raw(example=["조용한", "데이트"]),
        'review_rating': fields.Float(example=4.5),
        'review_num': fields.Integer(example=1),
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    user_review_detail = api.model('user_review_detail', {
        'review_id': fields.Integer(example=1),
        'place_id': fields.Integer(example=1),
        'name': fields.String,
        'rating': fields.Float(example=4.5),
        'content': fields.String,
        'review_img': fields.String(example=["http://owncourse.seongbum.com/static/uploads/reviewIMG.jpeg"]),
        'likes': fields.Integer(example=1),
        'source': fields.String(example='owncourse'),
        'created_at': fields.DateTime(example='yyyy-mm-dd hh:mm:ss'),
        'distance': fields.Float(example=300.5)
    })
    user_review = api.model('user_review', {
        'review_num': fields.Integer(example=1),
        'result': fields.List(fields.Nested(user_review_detail))
    })
    user_notification = api.model('user_notification', {
        'review_id': fields.Integer(example=1),
        'user_id': fields.Integer(example=1),
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
        'id': fields.Integer(example=1),
        'name': fields.String,
        'categories': fields.Raw(example=["FD1"]),
        'large_categories': fields.Raw(example=["FD"]),
        'like': fields.Boolean,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    place_by_category = api.model('place_by_category', {
        'id': fields.Integer(example=1),
        'name': fields.String,
        'address': fields.String,
        'categories': fields.Raw(example=["음료전문"]),
        'hashtags': fields.Raw(example=["조용한", "데이트"]),
        'distance': fields.Float(example=300.5),
        'review_rating': fields.Float(example=4.5),
        'review_num': fields.Integer(example=1),
        'like': fields.Boolean,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    place_description = api.model('place_description', {
        'source': fields.String(example="카카오맵"),
        'description': fields.String
    })
    place_detail = api.model('place_detail', {
        'id': fields.Integer(example=1),
        'name': fields.String,
        'address': fields.String,
        'road_address': fields.String,
        'categories': fields.Raw(example=["음료전문"]),
        'hashtags': fields.Raw(example=["조용한", "데이트"]),
        'phone': fields.String,
        'longitude': fields.Float(example=37.5),
        'latitude': fields.Float(example=120.7),
        'descriptions': fields.List(fields.Nested(place_description)),
        'review_rating': fields.Float(example=4.5),
        'review_num': fields.Integer(example=1),
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
        'rating': fields.Float(example=4.5, description='Review rating'),
        'content': fields.String(description='Review content')
    })
    review_id = api.model('review_id', {
        'id': fields.Integer(example=1)
    })
    review_detail = api.model('review_detail', {
        'id': fields.Integer(example=1),
        'user_id': fields.Integer(example=1),
        'place_id': fields.Integer(example=1),
        'rating': fields.Float(example=4.5),
        'content': fields.String,
        'review_img': fields.Raw(example=["http://owncourse.seongbum.com/static/uploads/reviewIMG.jpeg"]),
        'like_num': fields.Integer(example=1),
        'source': fields.String,
        'created_at': fields.DateTime(example='yyyy-mm-dd hh:mm:ss'),
        'user_name': fields.String,
        'profile_img': fields.String(example="http://owncourse.seongbum.com/static/uploads/profileIMG.jpeg"),
        'like': fields.Boolean
    })
    review_img_detail = api.model('review_img_detail', {
        'review_id': fields.Integer(example=1),
        'rating': fields.Float(example=4.5),
        'review_img': fields.Raw(example=["http://owncourse.seongbum.com/static/uploads/reviewIMG.jpeg"])
    })
    review_error = api.model('review_error', {
        'message': fields.String
    })
    review_by_place = api.model('review_by_place', {
        'review_num': fields.Integer(example=1),
        'result': fields.List(fields.Nested(review_detail))
    })
    review_img = api.model('review_img', {
        'review_num': fields.Integer(example=1),
        'review_img_num': fields.Integer(example=1),
        'result': fields.List(fields.Nested(review_img_detail))
    })
    review_like = api.model('review_like', {
        'like': fields.Boolean
    })


class CourseDto:
    api = Namespace('Course', description='코스')
    course_id = api.model('course_id', {
        'course_id': fields.Integer(example=1)
    })
    course_info = api.model('course_info', {
        'place_id': fields.Integer(example=1),
        'place_order': fields.Integer(example=1)
    })
    course_place_description = api.model('course_place_description', {
        'source': fields.String(example="카카오맵"),
        'description': fields.String
    })
    course_recommend = api.model('course_recommend', {
        'id': fields.Integer(example=1),
        'name': fields.String,
        'categories': fields.Raw(example=["FD1"]),
        'latitude': fields.Float(example=37.5),
        'longitude': fields.Float(example=120.7),
        'large_categories': fields.Raw(example=["FD"]),
        'avg_price': fields.Integer(example=20000),
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
        'review_num': fields.Integer(example=1),
        'hashtags': fields.Raw(example=["조용한", "데이트"])
    })
    course = api.model('course', {
        'course_name': fields.String,
        'place_num': fields.Integer(example=1),
        'cost': fields.Integer(example=20000),
        'hours': fields.Float(example=3.5),
        'address': fields.String,
        'longitude': fields.Float(example=37.5),
        'latitude': fields.Float(example=120.7),
        'course_info': fields.List(fields.Nested(course_info), action='append', description='장소 개수 만큼 입력')
    })
    course_list = api.model('course_list', {
        'id': fields.Integer(example=1),
        'course_name': fields.String,
        'cost': fields.Integer(example=20000),
        'hours': fields.Float(example=3.5),
        'address': fields.String,
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    course_detail = api.model('course_detail', {
        'place_id': fields.Integer(example=1),
        'place_order': fields.Integer(example=1),
        'avg_cost': fields.Integer(example=20000),
        'popular_menu': fields.String,
        'name': fields.String,
        'address': fields.String,
        'road_address': fields.String,
        'categories': fields.String(example=["음료전문"]),
        'hashtags': fields.String(example=["조용한", "데이트"]),
        'phone': fields.String,
        'longitude': fields.Float(example=37.5),
        'latitude': fields.Float(example=120.7),
        'descriptions': fields.List(fields.Nested(course_place_description)),
        'like': fields.Boolean,
        'review_rating': fields.Float(example=4.5),
        'review_num': fields.Integer(example=1),
        'img_url': fields.String(example="http://owncourse.seongbum.com/static/uploads/FD1.jpeg")
    })
    course_error = api.model('course_error', {
        'message': fields.String
    })
