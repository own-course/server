import json
import random


def reviewDetail(row, database, root_url):
    row['created_at'] = json.dumps(row['created_at'].strftime('%Y-%m-%d %H:%M:%S'))
    if row['review_img'] is not None:
        imgs = row['review_img'][1:-1]
        imgs = imgs.split('","')
        review_img = []
        for img in imgs:
            review_img.append(root_url + img)
        row['review_img'] = review_img
    else:
        row['review_img'] = []
    if row['source'] != 'owncourse':
        if row['source'] == 'kakao_map':
            row['user_name'] = '카카오맵 사용자'
        else:
            row['user_name'] = None
        row['profile_img'] = None
    else:
        sql = """
            SELECT nickname, profile_img FROM Profile
            WHERE user_id = %(user_id)s
        """
        profile = database.execute_one(sql, {'user_id': row['user_id']})
        row['user_name'] = profile['nickname']
        if profile['profile_img'] is not None:
            row['profile_img'] = root_url + profile['profile_img']
        else:
            row['profile_img'] = None


def reviewRatingAndNum(row, place_id, database):
    sql = """
           SELECT AVG(Review.rating) AS rating, COUNT(Review.id) AS review_num
           FROM Review
           WHERE place_id = %(place_id)s      
    """
    review = database.execute_one(sql, {'place_id': place_id})
    if review['rating'] is None:
        row['review_rating'] = 0
        row['review_num'] = 0
    else:
        row['review_rating'] = review['rating']
        row['review_num'] = review['review_num']


def isLikedPlace(row, place_id, user_id, database):
    sql = """
        SELECT enabled FROM Place_User
        WHERE place_id = %(place_id)s AND user_id = %(user_id)s
    """
    like = database.execute_one(sql, {'place_id': place_id, 'user_id': user_id})
    if like is None:
        row['like'] = False
    else:
        if like['enabled'] == 0:
            row['like'] = False
        else:
            row['like'] = True


def categoryToCode(category):
    categories = category[2:-2].replace('","', "|")
    categories = categories.split('|')

    result = ""
    for category in categories:
        if category == "전체":
            result += "|ALL"
        elif category == "관광명소전체":
            result += "|AT"
        elif category == "공원":
            result += "|AT1"
        elif category == "야경/풍경":
            result += "|AT2"
        elif category == "식물원,수목원":
            result += "|AT3"
        elif category == "시장":
            result += "|AT4"
        elif category == "동물원":
            result += "|AT5"
        elif category == "지역축제":
            result += "|AT6"
        elif category == "유적지":
            result += "|AT7"
        elif category == "바다":
            result += "|AT8"
        elif category == "산/계곡":
            result += "|AT9"
        elif category == "음식점전체":
            result += "|FD"
        elif category == "한식":
            result += "|FD1"
        elif category == "중식":
            result += "|FD2"
        elif category == "분식":
            result += "|FD3"
        elif category == "일식":
            result += "|FD4"
        elif category == "패스트푸드":
            result += "|FD5"
        elif category == "아시안,양식":
            result += "|FD6"
        elif category == "치킨,피자":
            result += "|FD7"
        elif category == "세계음식":
            result += "|FD8"
        elif category == "채식":
            result += "|FD9"
        elif category == "해산물":
            result += "|FD10"
        elif category == "간식":
            result += "|FD11"
        elif category == "육류,고기":
            result += "|FD12"
        elif category == "기타":
            result += "|FD13"
        elif category == "카페전체":
            result += "|CE"
        elif category == "음료전문":
            result += "|CE1"
        elif category == "디저트전문":
            result += "|CE2"
        elif category == "테마카페":
            result += "|CE3"
        elif category == "룸카페":
            result += "|CE4"
        elif category == "이색체험전체":
            result += "|UE"
        elif category == "공방":
            result += "|UE1"
        elif category == "원데이클래스":
            result += "|UE2"
        elif category == "사진스튜디오":
            result += "|UE3"
        elif category == "사주/타로":
            result += "|UE4"
        elif category == "VR":
            result += "|UE5"
        elif category == "액티비티전체":
            result += "|AC"
        elif category == "게임/오락":
            result += "|AC1"
        elif category == "온천,스파":
            result += "|AC2"
        elif category == "레저스포츠":
            result += "|AC3"
        elif category == "테마파크":
            result += "|AC4"
        elif category == "아쿠아리움":
            result += "|AC5"
        elif category == "낚시":
            result += "|AC6"
        elif category == "캠핑":
            result += "|AC7"
        elif category == "방탈출":
            result += "|AC8"
        elif category == "노래방":
            result += "|AC9"
        elif category == "보드카페":
            result += "|AC10"
        elif category == "동물카페":
            result += "|AC11"
        elif category == "만화/북카페":
            result += "|AC912"
        elif category == "문화생활전체":
            result += "|CT"
        elif category == "영화":
            result += "|CT1"
        elif category == "전시회":
            result += "|CT2"
        elif category == "공연":
            result += "|CT3"
        elif category == "스포츠경기":
            result += "|CT4"
        elif category == "미술관":
            result += "|CT5"
        elif category == "박물관":
            result += "|CT6"
        elif category == "쇼핑":
            result += "|CT7"

    return result[1:]


def codeToCategory(category):
    categories = category[2:-2].replace('","', "|")
    categories = categories.split('|')

    i = 0
    result = []
    for category in categories:
        if i == 3:
            break

        if category == "AT1":
            result.append("공원")
        elif category == "AT2":
            result.append("야경/풍경")
        elif category == "AT3":
            result.append("식물원,수목원")
        elif category == "AT4":
            result.append("시장")
        elif category == "AT5":
            result.append("동물원")
        elif category == "AT6":
            result.append("지역축제")
        elif category == "AT7":
            result.append("유적지")
        elif category == "AT8":
            result.append("바다")
        elif category == "AT9":
            result.append("산/계곡")
        elif category == "FD1":
            result.append("한식")
        elif category == "FD2":
            result.append("중식")
        elif category == "FD3":
            result.append("분식")
        elif category == "FD4":
            result.append("일식")
        elif category == "FD5":
            result.append("패스트푸드")
        elif category == "FD6":
            result.append("아시안,양식")
        elif category == "FD7":
            result.append("치킨,피자")
        elif category == "FD8":
            result.append("세계음식")
        elif category == "FD9":
            result.append("채식")
        elif category == "FD10":
            result.append("해산물")
        elif category == "FD11":
            result.append("간식")
        elif category == "FD12":
            result.append("육류,고기")
        elif category == "FD13":
            result.append("기타")
        elif category == "CE1":
            result.append("음료전문")
        elif category == "CE2":
            result.append("디저트전문")
        elif category == "CE3":
            result.append("테마카페")
        elif category == "CE4":
            result.append("룸카페")
        elif category == "UE1":
            result.append("공방")
        elif category == "UE2":
            result.append("원데이클래스")
        elif category == "UE3":
            result.append("사진스튜디오")
        elif category == "UE4":
            result.append("사주/타로")
        elif category == "UE5":
            result.append("VR")
        elif category == "AC1":
            result.append("게임/오락")
        elif category == "AC2":
            result.append("온천,스파")
        elif category == "AC3":
            result.append("레저스포츠")
        elif category == "AC4":
            result.append("테마파크")
        elif category == "AC5":
            result.append("아쿠아리움")
        elif category == "AC6":
            result.append("낚시")
        elif category == "AC7":
            result.append("캠핑")
        elif category == "AC8":
            result.append("방탈출")
        elif category == "AC9":
            result.append("노래방")
        elif category == "AC10":
            result.append("보드카페")
        elif category == "AC11":
            result.append("동물카페")
        elif category == "AC12":
            result.append("만화/북카페")
        elif category == "CT1":
            result.append("영화")
        elif category == "CT2":
            result.append("전시회")
        elif category == "CT3":
            result.append("공연")
        elif category == "CT4":
            result.append("스포츠경기")
        elif category == "CT5":
            result.append("미술관")
        elif category == "CT6":
            result.append("박물관")
        elif category == "CT7":
            result.append("쇼핑")
        i += 1

    return result


def hashtagToArray(hashtag):
    char = "[\" ]"
    for removeChar in char:
        hashtag = hashtag.replace(removeChar, "")
    hashtags = hashtag.split(',')

    return hashtags


def descriptionToArray(description):
    descriptions = description[2:-2].replace('},{', "|")
    descriptions = descriptions.split('|')

    return descriptions


def keywordToVector(keyword, vector):
    idx = 0
    if keyword == "세련":
        idx = 0
    elif keyword == "독특":
        idx = 1
    elif keyword == "아기자기":
        idx = 2
    elif keyword == "모던":
        idx = 3
    elif keyword == "깔끔":
        idx = 4
    elif keyword == "아늑":
        idx = 5
    elif keyword == "귀엽":
        idx = 6
    elif keyword == "깨끗":
        idx = 7
    elif keyword == "클래식":
        idx = 8
    elif keyword == "고급":
        idx = 9
    elif keyword == "아담":
        idx = 10
    elif keyword == "조용":
        idx = 11
    elif keyword == "따뜻":
        idx = 12
    elif keyword == "포근":
        idx = 13
    vector[idx] = 1

    return vector


def imgSelect(category):
    if type(category) == str:
        category = category[2:4]
    else:
        category = category[0][0:2]

    root_url = "http://owncourse.seongbum.com/static/uploads/"
    url = ""

    if category == "FD":
        num = random.randint(1, 4)
        url = root_url + "FD" + str(num) + ".jpeg"
    elif category == "CE":
        num = random.randint(1, 4)
        url = root_url + "CE" + str(num) + ".jpeg"
    elif category == "AT":
        num = random.randint(1, 6)
        url = root_url + "AT" + str(num) + ".jpeg"
    elif category == "CT":
        num = random.randint(1, 2)
        url = root_url + "CT" + str(num) + ".jpeg"
    elif category == "AC":
        num = random.randint(1, 3)
        url = root_url + "AC" + str(num) + ".jpeg"
    elif category == "UE":
        num = random.randint(1, 1)
        url = root_url + "UE" + str(num) + ".jpeg"

    return url
