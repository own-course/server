from flask import make_response, request
from flask_restx import Resource
from util.dto import PlaceDto
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.database import Database
from util.upload import upload_file
from util.utils import categoryToCode, codeToCategory, hashtagToArray, descriptionToArray, imgSelect
from util.recommend import recommend_poi

place = PlaceDto.api
_place_recommend = PlaceDto.place_recommend
_place_by_category = PlaceDto.place_by_category
_place_detail = PlaceDto.place_detail
_place_like = PlaceDto.place_like
_place_error = PlaceDto.place_error

@place.doc(params={
    'latitude': {'description': 'latitude', 'in': 'query', 'type': 'float'},
    'longitude': {'description': 'longitude', 'in': 'query', 'type': 'float'}
})
@place.route('/recommend')
@place.response(200, 'Success', [_place_recommend])
class RecommendPlaceAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)
        
        parser = api.parser()
        parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('longitude', type=float, required=True)
        args = parser.parse_args()

        self.user_id = get_jwt_identity()
        self.latitude = args['latitude']
        self.longitude = args['longitude']
        self.distance = 500 # 반경 500m

    @place.doc(security='apiKey')
    def get(self):
        """홈 탭의 추천 장소"""
        rec_poi_list = recommend_poi(self.user_id, self.latitude, self.longitude, self.distance)

        database = Database()
        place = []
        i = 0
        for item in rec_poi_list:
            if i == 10:
                break
            i += 1
            del item['taste'], item['service'], item['cost'], item['tsc_score']
            del item['distance'], item['latitude'], item['longitude']

            value = {
                'place_id': item['id'],
                'user_id': self.user_id
            }
            sql = """
                SELECT enabled FROM Place_User
                WHERE place_id = %(place_id)s AND user_id = %(user_id)s
            """
            like = database.execute_one(sql, value)
            if like is None:
                item['like'] = False
            else:
                if like['enabled'] == 0:
                    item['like'] = False
                else:
                    item['like'] = True
            item['img_url'] = imgSelect(item['categories'])
            place.append(item)

        database.close()

        return place, 200

@place.doc(params={
    'sort': {'description': 'location, popular or taste', 'in': 'query', 'type': 'string'},
    'page':
            {'description': 'pagination (start=1) 10개씩 반환', 'in': 'query', 'type': 'int'},
    'category': {'description': '배열로 입력 ex) ["전체"] or ["관광명소전체"] or ["관광명소전체","음식점전체","디저트전문",'
                                '"공방","전시회"]\n\n'
                                '관광명소: "관광명소전체", "공원", "야경/풍경", "식물원,수목원", "시장", "동물원", "지역축제", '
                                '"유적지", "바다", "산/계곡"\n\n'
                                '음식점: "음식점전체", "한식", "중식", "분식", "일식", "패스트푸드", "아시안,양식", "치킨,피자", '
                                '"세계음식", "채식", "해산물", "간식", "육류,고기", "기타"\n\n'
                                '카페: "카페전체", "음료전문", "디저트전문", "테마카페", "보드카페", "동물카페", "만화/북카페", '
                                '"룸카페"\n\n'
                                '이색체험: "이색체험전체", "공방", "원데이클래스", "사진스튜디오", "사주/타로", "VR", "방탈출", '
                                '"노래방"\n\n'
                                '액티비티: "액티비티전체", "게임/오락", "온천,스파", "레저스포츠", "테마파크", "아쿠아리움", '
                                '"낚시", "캠핑"\n\n'
                                '문화생활: "문화생활전체", "영화", "전시회", "공연", "스포츠경기", "미술관", "박물관", "쇼핑"\n\n',
                 'in': 'query', 'type': 'raw'},
    'latitude':
        {'description': 'latitude', 'in': 'query', 'type': 'float'},
    'longitude':
        {'description': 'longitude', 'in': 'query', 'type': 'float'},
    'search':
        {'description': 'search by place name or place address or place hastags', 'in': 'query', 'type': 'string'}
})
@place.route('')
@place.response(200, 'Success', [_place_by_category])
@place.response(400, 'Bad Request', _place_error)
class PlacesByCategoryAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        parser = api.parser()
        parser.add_argument('sort', type=str, required=True)
        parser.add_argument('page', type=int, required=True)
        parser.add_argument('category', type=str, required=True)
        parser.add_argument('latitude', type=float, required=True)
        parser.add_argument('longitude', type=float, required=True)
        parser.add_argument('search', type=str, required=False)
        args = parser.parse_args()

        self.sort = args['sort']
        self.page = args['page']
        self.category = args['category']
        self.longitude = args['longitude']
        self.latitude = args['latitude']
        self.search = args['search']
        self.distance = 500
        self.user_id = get_jwt_identity()

    @place.doc(security='apiKey')
    def get(self):
        """카테고리별 장소"""
        database = Database()
        category = categoryToCode(self.category)
        page = self.page - 1
        limit = 10
        value = {
            'sort': self.sort,
            'category': category,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'search': self.search,
            'start': page * limit,
            'limit': limit
        }

        if self.sort == "taste":
            rec_poi_list = recommend_poi(self.user_id, self.latitude, self.longitude, self.distance)
            rows = []
            if category == 'ALL':
                if self.search is None:
                    for i in range(page, page + limit):
                        sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1 AND id = %(place_id)s
                        """
                        value['place_id'] = rec_poi_list[i]['id']
                        row = database.execute_one(sql, value)
                        rows.append(row)
                else:
                    sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1 
                            AND name REGEXP %(search)s OR address REGEXP %(search)s OR hashtags REGEXP %(search)s
                            ORDER BY distance
                            LIMIT %(start)s, %(limit)s
                    """
                    rows = database.execute_all(sql, value)
            else:
                if self.search is None:
                    # places = []
                    # for item in rec_poi_list:
                    #     sql = """
                    #         SELECT id, name, address, categories, hashtags,
                    #         (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                    #         * cos(radians(Place.longitude) - radians(%(longitude)s))
                    #         + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                    #         FROM Place
                    #         WHERE enabled = 1 AND id = %(place_id)s AND categories REGEXP %(category)s
                    #     """
                    #     value['place_id'] = item['id']
                    #     row = database.execute_one(sql, value)
                    #     if row is not None:
                    #         places.append(row)
                    # for i in range(page, page + limit):
                    #     rows.append(places[i])
                    sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1
                            AND categories REGEXP %(category)s
                            ORDER BY distance
                            LIMIT %(start)s, %(limit)s
                    """
                    rows = database.execute_all(sql, value)
                else:
                    sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1
                            AND categories REGEXP %(category)s 
                            AND name REGEXP %(search)s OR address REGEXP %(search)s OR hashtags REGEXP %(search)s
                            ORDER BY distance
                            LIMIT %(start)s, %(limit)s
                    """
                    rows = database.execute_all(sql, value)
        else:
            if category == 'ALL':
                if self.search is None:
                    sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1
                            ORDER BY distance
                            LIMIT %(start)s, %(limit)s
                    """
                else:
                    sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1 
                            AND name REGEXP %(search)s OR address REGEXP %(search)s OR hashtags REGEXP %(search)s
                            ORDER BY distance
                            LIMIT %(start)s, %(limit)s
                    """
            else:
                if self.search is None:
                    sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1
                            AND categories REGEXP %(category)s
                            ORDER BY distance
                            LIMIT %(start)s, %(limit)s
                    """
                else:
                    sql = """
                            SELECT id, name, address, categories, hashtags,
                            (6371000 * acos(cos(radians(%(latitude)s)) * cos(radians(Place.latitude))
                            * cos(radians(Place.longitude) - radians(%(longitude)s))
                            + sin(radians(%(latitude)s)) * sin(radians(Place.latitude)))) AS distance
                            FROM Place
                            WHERE enabled = 1
                            AND categories REGEXP %(category)s 
                            AND name REGEXP %(search)s OR address REGEXP %(search)s OR hashtags REGEXP %(search)s
                            ORDER BY distance
                            LIMIT %(start)s, %(limit)s
                    """
            rows = database.execute_all(sql, value)
        for row in rows:
            sql = """
                    SELECT AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num
                    FROM Review
                    WHERE place_id = %(place_id)s      
            """
            review = database.execute_one(sql, {'place_id': row['id']})
            if review['rating'] is None:
                row['review_rating'] = 0
                row['review_num'] = 0
            else:
                row['review_rating'] = review['rating']
                row['review_num'] = review['review_num']
        for row in rows:
            sql = """
                SELECT enabled FROM Place_User
                WHERE place_id = %(place_id)s AND user_id = %(user_id)s
            """
            like = database.execute_one(sql, {'place_id': row['id'], 'user_id': self.user_id})
            if like is None:
                row['like'] = False
            else:
                if like['enabled'] == 0:
                    row['like'] = False
                else:
                    row['like'] = True
        for row in rows:
            row['img_url'] = imgSelect(row['categories'])
            categories = codeToCategory(row['categories'])
            if row['hashtags'] is not None:
                row['hashtags'] = hashtagToArray(row['hashtags'])
            row['categories'] = categories

        if self.sort == "location" or self.sort == "taste":
            database.close()
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

            result = sorted(rows, key=lambda x: str(x['review_rating'])[:3], reverse=True)
            database.close()

            return result, 200

        else:
            database.close()

            return make_response({'message': 'Invalid request.'}, 400)

@place.route('/<int:place_id>')
@place.response(200, 'Success', _place_detail)
@place.response(400, 'Bad Request', _place_error)
class PlaceInfoAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        self.user_id = get_jwt_identity()

    @place.doc(security='apiKey')
    def get(self, place_id):
        """장소 상세정보"""
        database = Database()
        sql = """
            SELECT id, name, address, road_address, categories, hashtags,
            phone, longitude, latitude, descriptions
            FROM Place
            WHERE id = %(place_id)s AND enabled = 1
        """
        row = database.execute_one(sql, {'place_id': place_id})

        if row is None:
            database.close()

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
            sql = """
                SELECT enabled FROM Place_User
                WHERE place_id = %(place_id)s AND user_id = %(user_id)s
            """
            like = database.execute_one(sql, {'place_id': row['id'], 'user_id': self.user_id})
            if like is None:
                row['like'] = False
            else:
                if like['enabled'] == 0:
                    row['like'] = False
                else:
                    row['like'] = True
            row['img_url'] = imgSelect(row['categories'])
            categories = codeToCategory(row['categories'])
            row['categories'] = categories
            if row['hashtags'] is not None:
                row['hashtags'] = hashtagToArray(row['hashtags'])
            if row['descriptions'] != "[]":
                description = []
                row['descriptions'] = descriptionToArray(row['descriptions'])
                for item in row['descriptions']:
                    list = {}
                    items = item.split(',"description":')
                    list['source'] = items[0][9:]
                    list['description'] = items[1]
                    description.append(list)
                row['descriptions'] = description
            else:
                row['descriptions'] = []

        database.close()

        return row, 200

@place.route('/<int:place_id>/like')
@place.response(200, 'Success', _place_like)
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
            database.close()

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
            like = True
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
                    like = False
                elif row['enabled'] == 0:
                    sql = """
                        UPDATE Place_User SET enabled = 1
                        WHERE place_id = %(place_id)s AND user_id = %(user_id)s
                    """
            database.execute(sql, value)
            database.commit()
            database.close()

            return {"like": like}, 200


@place.route('/img')
class uploadPlaceImgAPI(Resource):
    @jwt_required()
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

        self.user_id = get_jwt_identity()

    @place.doc(security='apiKey')
    @place.response(200, 'Success')
    def post(self):
        """장소 사진 등록 (임시)"""
        result = upload_file(request.files)
        if result['message'] == 'Success':
            return {'filename': result['filename'][:-1]}, 200
        else:
            return {'message': result['message']}, 400
