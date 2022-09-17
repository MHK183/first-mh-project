import pandas as pd
import folium
import numpy as np
from folium import plugins

# 필요없는 자료 정리
def remove(data):
    data.drop('Unnamed: 0_level_0', axis=1, level=0, inplace=True)
    data.drop(0, axis=0, inplace=True)
    data.rename(columns={'일시(KST)  오름차순정렬': '일시(KST)'}, level=0, inplace=True)
    data.rename(columns={'일시(KST)  오름차순정렬': '일시(KST)'}, level=1, inplace=True)


# 멀티 컬럼 정리하기
def columns(data):
    new_columns = []  # 신규 컬럼명 생성
    for col1, col2 in data.columns:
        if col1 == col2:
            new_column_name = col2
            new_columns.append(new_column_name)
        else:
            new_column_name = f"{col1}_{col2}"
            new_columns.append(new_column_name)
    data.columns = new_columns  # 컬럼명 변경하기


# 인덱스 설정 후 정렬하기
def set_sort(data):
    data.set_index('일시(KST)', inplace=True)
    data.sort_index(ascending=True, inplace=True)

def draw_typoon(data):
    global korea_map
    points = []
    wind_ranges = []

    for time, max_speed, power, lat, lng, hpa, wind_range in zip(data.index, data['최대풍속_초속(m/s)'],
                                                                 data['강도'], data['중심위치_위도(°N)'],
                                                                 data['중심위치_경도(°E)'], data['중심기압_(hPa)'],
                                                                 data['강풍반경_(km)']):
        folium.CircleMarker([lat, lng],
                            radius=3,
                            color='black',
                            fill=True,
                            fill_color='red',
                            fill_opacity=0.7,
                            popup=(f'위도{lat} 경도{lng}', f'{time}시', f'{max_speed} m/s({int(hpa)} hPa) {power}',
                                   f'강풍반경 : {wind_range} km')
                            ).add_to(korea_map)
        a = {}
        a['time'] = time
        a['coordinates'] = [lng, lat]
        a['radius'] = int(wind_range)
        points.append(a)
        wind_ranges.append(wind_range)

    features = [
        {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': point['coordinates'],
            },
            'properties': {
                'time': point['time'],
                'style': {'color': '#3186cc'},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': 'skyblue',
                    'fillOpacity': 0.1,
                    'stroke': 'false',
                    'radius': point['radius'] / 10
                }
            }
        } for point in points
    ]

    plugins.TimestampedGeoJson(
        {
            'type': 'FeatureCollection',
            'features': features
        },
        transition_time=200,
        period='PT3H',
        add_last_point=True,
        auto_play=False,
        loop=False,
        max_speed=1,
        loop_button=True,
        date_options='YYYY/MM/DD HH:mm',
        time_slider_drag_update=True,
        duration='PT9H'
    ).add_to(korea_map)

    return korea_map


# 태풍 피해금액이 있는 리스트
damages = [200205, 200215, 200306, 200314, 200415, 200418, 200514, 200610,
           200613, 200704, 200711, 200807, 201004, 201007, 201009, 201109,
           201207, 201215, 201216, 201324, 201408, 201515, 201618, 201819,
           201825, 201905, 201913, 201917, 201918, 202008]

typoon_list = pd.read_excel('./태풍 리스트 2000~2022.xlsx', header=0).astype('str')

typoon_list.set_index('태풍번호', inplace=True)

# 입력
# 불러오고 싶은 자료 입력하기 ( 2001년 부터 )

num = input("불러오고 싶은 태풍번호를 입력하세요 ex)200101 : ")

# 자료 불러오기

number = num
name = typoon_list.loc[num, '태풍명']
sebu = pd.read_excel(f'./태풍 세부정보/{number}_{name}.xlsx', header=[0, 1])

# 태풍 피해금액 리스트에 포함된 태풍일경우에만 실행
if int(num) in damages:
    damage = pd.read_excel(f'./typoon_damage/{number}_{name}.xlsx')

# 자료 정리
remove(sebu)

# 컬럼명 정리하기
columns(sebu)

# 인덱스 설정 후 정렬하기
set_sort(sebu)

# 누락 데이터 제거
sebu.replace('-', np.nan, inplace=True)
sebu = sebu.dropna(subset=['강풍반경_(km)'], how='any', axis=0)

# 대한민국 기준 지도 보여주기
korea_map = folium.Map(location=[30.55, 130.98], zoom_start=4, tiles='Stamen Terrain')

# 태풍 경로 그리기 (태풍 경로 및 경로 이동은 2001년부터)
draw_typoon(sebu)

print(f'{number}_{name}');
print("=" * 30)

# 피해금액이 있는 태풍일 경우에만 출력
if int(num) in damages:
    print('총 피해금액 : ', damage['합계'].max());
    print("=" * 30)
print(sebu)
korea_map.save(f'./{number}_{name}.html')
