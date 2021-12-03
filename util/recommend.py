from database.database import Database
import json

def recommend_poi(user_id, latitude, longitude, distance):
    sql = '''
        SELECT
            a.id,
            a.name,
            a.categories,
            b.taste,
            b.service,
            b.cost,
            b.taste*c.t + b.service*c.s + b.cost*c.c AS tsc_score,
            (6371000*acos(cos(radians(%(latitude)s))*cos(radians(a.latitude))*cos(radians(a.longitude)
                - radians(%(longitude)s)) + sin(radians(%(latitude)s))*sin(radians(a.latitude))))
                AS distance,
            a.latitude,
            a.longitude
        FROM
            Place a,
            Place_TSCA b,
            Profile c
        WHERE
            a.id = b.place_id
            AND a.enabled = 1
            AND c.user_id = %(user_id)s
        HAVING distance <= %(distance)s
        ORDER BY tsc_score DESC, distance ASC
    '''

    values = {
        'latitude': latitude,
        'longitude': longitude,
        'user_id': user_id,
        'distance': distance
    }
    
    database = Database()
    database.cursor.execute(sql, values)
    data = database.cursor.fetchall()
    database.close()
    
    for item in data:
        # TSC 점수 자료형 변환
        item['tsc_score'] = float(item['tsc_score'])

        # 카테고리 list
        item['categories'] = json.loads(item['categories'])
        item['large_categories'] = []
        for category in item['categories']:
            lc = category[:2]
            if lc not in item['large_categories']:
                item['large_categories'].append(lc)
    
    return data