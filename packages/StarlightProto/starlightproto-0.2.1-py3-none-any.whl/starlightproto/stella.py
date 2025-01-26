# 필요 패키지 import
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
from astropy.time import Time
import numpy as np
import typer


#test 데이터
countries = ["korea", "korea2"]
constellations = ["Leo", "Leo2"]

# 첫 입력에 따른 행동 구분
def select_act(keyword: str, sub1: str=None, sub2: str=None):
    if keyword == "search_c":
        search_c_act(sub1)
    elif keyword == "search_s":
        search_s_act(sub1)
    elif keyword == "find":
        find_act(sub1, sub2)

# 저장된 국가 검색 함수
def search_c_act(sub1: str=None):
    if sub1:
        result = [country for country in countries if sub1.lower() in country.lower()]
        if result:
            print(f"{sub1}에 대한 검색 결과 : {result}")
            return result
        else: 
            print("검색 결과가 없습니다")
            return None
    else:
        #print(f"저장된 국가 리스트 : {countries}")
        return print(f"저장된 국가 리스트 : {countries}")

# 저장된 별자리 검색 함수
def search_s_act(sub1: str=None):
    if sub1:
        result = [stella for stella in constellations if sub1.lower() in stella.lower()]
        if result:
            print(f"{sub1}에 대한 검색 결과 : {result}")
        else: print("검색 결과가 없습니다")
    else:
        print(f"저장된 별자리 리스트 : {constellations}")

def find_act(sub1_location: str, sub2_constellation: str):
    
    # 사용자 정보 입력
    latitude = 37.5665
    longitude = 126.9780
    altitude = 0 #고도는 0으로 통일
    ra = "10h30m"
    de = "+20d"
    date_time = "2025-01-25 12:00:00"

    #관측 위치 설정
    location = EarthLocation(lat=latitude, lon=longitude, height=altitude)

    #시각에 따른 관측 천구 생성
    observation_time = Time(date_time)
    altaz_frame = AltAz(obstime=observation_time, location=location) #관측 천구

    #별자리 위치 정보 전달
    constellation = SkyCoord(ra=ra, dec=de, frame="icrs")

    #관측 위치에 따른 별자리의 고도와 방위각 계산
    altaz = constellation.transform_to(altaz_frame)
    altitude = altaz.alt.deg #고도
    azimuth = altaz.az.deg #방위각

    #결과 출력
    if not is_observable(latitude, constellation.dec.deg):
        print("현 위치에서 해당 별자리는 관측되지 않습니다")

    else:
        if altitude > 0:
            direction = get_direction(azimuth)
            print(f"현재 별자리는 {direction}쪽 하늘에 떠 있습니다. (고도: {altitude:.2f}°, 방위각: {azimuth:.2f}°)")
        else :
            delta_time = 0
            while altitude <= 0:
                delta_time += 1
                future_time = observation_time + delta_time / 1440
                altaz_frame_future = AltAz(obstime=future_time, location=location)
                altaz_future = constellation.transform_to(altaz_frame_future)
                altitude = altaz_future.alt.deg

                if delta_time > 1440:
                    print("현 위치에서 해당 별자리는 오늘 관측할 수 없습니다, Err")
                    break

            if altitude > 0:
                print(f"해당 별자리는 {delta_time//60}시 {delta_time%60}분 후에 떠오릅니다.")


#별자리 방위 방향 결정
def get_direction(azimuth):
    if 0 <= azimuth < 45 or 315 <= azimuth <= 360:
        return "북"
    elif 45 <= azimuth < 135:
        return "동"
    elif 135 <= azimuth < 225:
        return "남"
    elif 225 <= azimuth < 315:
        return "서"


#별자리 관측 가능 여부 확인
def is_observable(latitude, dec):
    #북반구
    if latitude >= 0 :
        max_dec = 90
        min_dec = latitude - 90
    #남반구
    else :
        max_dec = latitude + 90
        min_dec = -90
    return min_dec <= dec <= max_dec


def entry_point():
    typer.run(select_act)
