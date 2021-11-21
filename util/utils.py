def categoryToCode(category):
    categories = category[2:-2].replace('", "', "|")
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
        elif category == "식물원/수목원":
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
        elif category == "돈까스/회/일식":
            result += "|FD4"
        elif category == "패스트푸드":
            result += "|FD5"
        elif category == "아시안/양식":
            result += "|FD6"
        elif category == "치킨/피자":
            result += "|FD7"
        elif category == "세계음식":
            result += "|FD8"
        elif category == "채식":
            result += "|FD9"
        elif category == "카페전체":
            result += "|CE"
        elif category == "음료전문":
            result += "|CE1"
        elif category == "디저트전문":
            result += "|CE2"
        elif category == "테마카페":
            result += "|CE3"
        elif category == "보드카페":
            result += "|CE4"
        elif category == "애견카페":
            result += "|CE5"
        elif category == "만화/북카페":
            result += "|CE6"
        elif category == "룸카페":
            result += "|CE7"
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
        elif category == "방탈출":
            result += "|UE6"
        elif category == "노래방":
            result += "|UE7"
        elif category == "액티비티전체":
            result += "|AC"
        elif category == "게임/오락":
            result += "|AC1"
        elif category == "온천/스파":
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
