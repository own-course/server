from flask import make_response
from flask_restx import Resource
from util.dto import CourseDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database

course = CourseDto.api
_course_error = CourseDto.course_error

@course.doc(params={
    'category':
        {'description': 'category(if there are multiple, use with comma) (ex)AT1,CE,FD3,FD6', 'in': 'query', 'type': 'string'},
    'hours': {'description': 'hours in hours (ex)2', 'in': 'query', 'type': 'float'},
    'distance': {'description': 'distance in meters (ex)1500', 'in': 'query', 'type': 'int'},
    'cost': {'description': 'cost in won (ex)30000', 'in': 'query', 'type': 'int'},
    'longitude': {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'latitude': {'description': 'latitude', 'in': 'query', 'type': 'float'}
})
@course.route('/recommend')
@course.response(200, 'Success')
@course.response(400, 'Bad Request', _course_error)
class RecommendCourseAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('hours', type=float, required=True)
        parser.add_argument('distance', type=int, required=True)
        parser.add_argument('cost', type=int, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('latitude', type=float, required=True)
        args = parser.parse_args()

        self.category = args['category']
        self.hours = args['hours']
        self.distance = args['distance']
        self.cost = args['cost']
        self.longitude = args['longitude']
        self.latitude = args['latitude']

    @course.doc(security='apiKey')
    @jwt_required()
    def get(self):
        """코스 추천"""
        pass

@course.route('/<int:course_id>')
@course.response(200, 'Success')
@course.response(400, 'Bad Request', _course_error)
class SaveCourseAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @course.doc(security='apiKey')
    @jwt_required()
    def post(self, course_id):
        """코스 저장"""
        pass

@course.route('')
@course.response(200, 'Success')
@course.response(400, 'Bad Request', _course_error)
class GetSavedCourseAPI(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    @course.doc(security='apiKey')
    @jwt_required()
    def get(self):
        """저장한 내 코스 불러오기"""
        pass

