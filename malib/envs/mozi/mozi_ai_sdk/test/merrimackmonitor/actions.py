# 时间 ： 2020/8/15 20:16
# 作者 ： Dixit
# 文件 ： actions.py
# 项目 ： moziAIBT2
# 版权 ： 北京华戍防务技术有限公司

from malib.envs.mozi.mozi_ai_sdk.btmodel.bt import utils
import re
import random
from malib.envs.mozi.mozi_simu_sdk.mssnpatrol import CPatrolMission
from malib.envs.mozi.mozi_simu_sdk.mssnsupport import CSupportMission
from malib.envs.mozi.mozi_simu_sdk.mssnstrike import CStrikeMission
from malib.envs.mozi.mozi_ai_sdk.btmodel.bt.basic import *
from malib.envs.mozi.mozi_ai_sdk.btmodel.bt.detail import *

import geopy
from geopy import distance
from math import radians, cos, sin, asin, sqrt, degrees, atan2, degrees


def situationAwareness(scenario):
    side = scenario.get_side_by_name('蓝方')
    contacts = side.contacts
    targets = {k: v for k, v in contacts.items() if ('FFG530' in v.strName) or ('DDG173' in v.strName)}
    if len(targets) == 0:
        return False
    missionUnits = {k: v for k, v in side.aircrafts.items() if v.strAirOpsConditionString in [0, 19, 20, 21]}
    for unitGuid, unit in missionUnits.items():
        unitPos = {}
        unitPos['Latitude'] = unit.dLatitude
        unitPos['Longitude'] = unit.dLongitude
        for k, v in targets.items():
            if v.m_IdentificationStatus >= 3:
                disKilo = get_two_point_distance(unitPos['Longitude'], unitPos['Latitude'], v.dLongitude,
                                                 v.dLatitude)
                azimuth = get_azimuth((unitPos['Latitude'], unitPos['Longitude']), (v.dLatitude, v.dLongitude))
                # print('unit: ' + unit.strName, 'ship: ' + v.strName, 'azimuth: %f' % azimuth, 'currentHeading: %f' % unit.fCurrentHeading)
                if disKilo <= v.fAirRangeMax * 1.852 and abs(azimuth - unit.fCurrentHeading) < 90:  # 海里转公里需要乘以1.852
                    # 计算撤退点 TODO
                    doctrine = unit.get_doctrine()
                    doctrine.ignore_plotted_course('yes')
                    # unit.set_unit_heading(unit.fCurrentHeading + 180)
                    # retreatPos = get_point_with_point_bearing_distance(unitPos['Longitude'], unitPos['Latitude'],
                    #                                                    unit.fCurrentHeading + 180, 1)
                    retreatPos = get_end_point((unitPos['Latitude'], unitPos['Longitude']), 15, unit.fCurrentHeading + 180)
                    unit.plot_course([retreatPos])

def get_azimuth(geopoint1, geopoint2):
    """
    获取point1 指向 point2 的方位角
    :param geopoint1: tuple, (lat, lon), 例：(40.9, 140.0)
    :param geopoint2: tuple, (lat, lon), 例：(40.9, 142.0)
    :return: 角度 0-360, 正北：0， 正东:90, 顺时针旋转，正西：270
    """
    PI = 3.1415926535897932
    degree2radian = PI / 180.0
    lat1 = geopoint1[0] * degree2radian
    lon1 = geopoint1[1] * degree2radian
    lat2 = geopoint2[0] * degree2radian
    lon2 = geopoint2[1] * degree2radian
    azimuth = 180 * math.atan2(math.sin(lon2 - lon1),
                               math.tan(lat2) * math.cos(lat1) - math.sin(lat1) * math.cos(lon2 - lon1)) / PI
    return normal_angle(azimuth)

def normal_angle(angle):
    """
    角度调整为0-360度以内
    :param angle: float, 角度
    :return: float
    """
    if 0 <= angle < 360:
        return angle
    else:
        return angle % 360

def get_point_with_point_bearing_distance(lat, lon, bearing, distance):
    """
    一直一点求沿某一方向一段距离的点
    :param lat:纬度
    :param lon:经度
    :param bearing:朝向角
    :param distance:距离
    :return:
    """
    # pylog.info("lat:%s lon:%s bearing:%s distance:%s" % (lat, lon, bearing, distance))
    radiusEarthKilometres = 3440
    initialBearingRadians = radians(bearing)
    disRatio = distance / radiusEarthKilometres
    distRatioSine = sin(disRatio)
    distRatioCosine = cos(disRatio)
    startLatRad = radians(lat)
    startLonRad = radians(lon)
    startLatCos = cos(startLatRad)
    startLatSin = sin(startLatRad)
    endLatRads = asin((startLatSin * distRatioCosine) + (startLatCos * distRatioSine * cos(initialBearingRadians)))
    endLonRads = startLonRad + atan2(sin(initialBearingRadians) * distRatioSine * startLatCos,
                                     distRatioCosine - startLatSin * sin(endLatRads))
    my_lat = degrees(endLatRads)
    my_lon = degrees(endLonRads)
    # dic = {"latitude": my_lat, "longitude": my_lon}
    dic = (my_lat, my_lon)
    return dic

def get_end_point(geopoint1, distance, bearing):
    """

    :param geopoint1: 起点的经纬度
    :param distance:距离
    :param bearing:起点到终点的方位角
    :return:
    """
    PI = 3.1415926535897932
    degree2radian = PI / 180.0
    NM2KM = 1.852  # 海里转千米
    EARTH_RADIUS = 6371137  # 地球平均半径
    distance = distance * 1000
    lat1 = geopoint1[0] * degree2radian
    lon1 = geopoint1[1] * degree2radian
    brng = bearing * degree2radian
    lat2 = math.asin(math.sin(lat1) * math.cos(distance / EARTH_RADIUS) +
                     math.cos(lat1) * math.sin(distance / EARTH_RADIUS) * math.cos(brng))
    lon2 = lon1 + math.atan2(math.sin(brng) * math.sin(distance / EARTH_RADIUS) * math.cos(lat1),
                             math.cos(distance / EARTH_RADIUS) - math.sin(lat1) * math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return lat2, lon2

def get_distance_point(lat, lon, dis, direction):
    """
    根据经纬度，距离，方向获得一个地点
    :param lat: 纬度
    :param lon: 经度
    :param dis: 距离（千米）
    :param direction: 方向（北：0，东：90，南：180，西：360）
    :return:
    """
    start = geopy.Point(lat, lon)
    d = distance.VincentyDistance(kilometers=dis)
    d = d.destination(point=start, bearing=direction)
    print(d.latitude, d.longitude)
    dic = {"latitude": d.latitude, "longitude": d.longitude}
    return dic
# print(get_distance_point(33.0625105185452, 44.6287913650984, 40, 325))
# latitude='33.3681951159897', longitude='44.3768440602801'

def get_two_point_distance(lon1, lat1, lon2, lat2):
    pos1 = (lat1, lon1)
    pos2 = (lat2, lon2)
    dis = distance.vincenty(pos1, pos2)
    return dis.kilometers

def get_air_contacts(contacts):
    AirContacts = {}
    for k, v in contacts.items():
        if v.m_ContactType == 0:
            AirContacts[k] = v
    return AirContacts


def FindBoundingBoxForGivenContacts(contacts, defaults, padding):
    #  Variables
    coordinates = [btBas.MakeLatLong(defaults['AI-AO-1']['latitude'], defaults['AI-AO-1']['longitude']),
                   btBas.MakeLatLong(defaults['AI-AO-2']['latitude'], defaults['AI-AO-2']['longitude']),
                   btBas.MakeLatLong(defaults['AI-AO-3']['latitude'], defaults['AI-AO-3']['longitude']),
                   btBas.MakeLatLong(defaults['AI-AO-4']['latitude'], defaults['AI-AO-4']['longitude'])]
    contactBoundingBox = FindBoundingBoxForGivenLocations(coordinates, 0)
    contactCoordinates = []

    for k, v in contacts.items():
        contact = {}
        contact['latitude'] = v.dLatitude
        contact['longitude'] = v.dLongitude
        contactCoordinates.append(btBas.MakeLatLong(contact['latitude'], contact['longitude']))

    # Get Hostile Contact Bounding Box
    if len(contactCoordinates) > 0:
        contactBoundingBox = FindBoundingBoxForGivenLocations(contactCoordinates, padding)

    # Return Bounding Box
    return contactBoundingBox

def FindBoundingBoxForGivenLocations(coordinates, padding):
    west = 0.0
    east = 0.0
    north = 0.0
    south = 0.0

    # Condiation Check
    if coordinates is None or len(coordinates) == 0:
        padding = 0

    # Assign Up to numberOfReconToAssign
    for lc in range(0, len(coordinates)):
        loc = coordinates[lc]
        if lc == 0:
            north = loc['latitude']
            south = loc['latitude']
            west = loc['longitude']
            east = loc['longitude']
        else:
            if loc['latitude'] > north:
                north = loc['latitude']
            elif loc['latitude'] < south:
                south = loc['latitude']

            if loc['longitude'] < west:
                west = loc['longitude']
            elif loc['longitude'] > east:
                east = loc['longitude']

    # Adding Padding
    north = north + padding
    south = south - padding
    west = west - padding
    east = east + padding

    # Return In Format
    return [MakeLatLong(north, west), MakeLatLong(north, east), MakeLatLong(south, east), MakeLatLong(south, west)]

def MakeLatLong(latitude, longitude):
    instance = {'latitude': InternationalDecimalConverter(latitude),
                'longitude': InternationalDecimalConverter(longitude)}
    return instance


# 三维地球上两点中间的坐标
def MidPointCoordinate(lat1, lon1, lat2, lon2):
    # initialize
    lat1 = InternationalDecimalConverter(lat1)
    lon1 = InternationalDecimalConverter(lon1)
    lat2 = InternationalDecimalConverter(lat2)
    lon2 = InternationalDecimalConverter(lon2)
    dLon = math.radians(lon2 - lon1)
    # convert to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)

    Bx = math.cos(lat2) * math.cos(dLon)
    By = math.cos(lat2) * math.sin(dLon)
    lat3 = math.atan2(math.sin(lat1) + math.sin(lat2),
                      math.sqrt((math.cos(lat1) + Bx) * (math.cos(lat1) + Bx) + By * By))
    lon3 = lon1 + math.atan2(By, math.cos(lat1) + Bx)

    return MakeLatLong(math.degrees(lat3), math.degrees(lon3))

# a1_aaw_miss_1
def AttackDoctrineCreateAirMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    defaultRef = ['AI-AO-1', 'AI-AO-2', 'AI-AO-3', 'AI-AO-4']
    defaults = {v.strName: {'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in side.referencepnts.items()
                if v.strName in defaultRef}
    airContacts_dic = {k: v for k, v in side.contacts.items() if v.m_ContactType == 0}      # 探测到的敌方飞机
    airs_dic = side.aircrafts       # 本方所有飞机
    patrolmssn = [v for _, v in side.patrolmssns.items() if v.strName == 'a1_aaw_miss_1']
    if len(patrolmssn) == 1 or len(airs_dic) == 0 or len(airContacts_dic) == 0:
        return False

    hostileContactBoundingBox = FindBoundingBoxForGivenContacts(airContacts_dic, defaults, 3)
    zone = ['a1_aaw_miss_1_rp_1', 'a1_aaw_miss_1_rp_2', 'a1_aaw_miss_1_rp_3', 'a1_aaw_miss_1_rp_4']
    side.add_reference_point('蓝方', zone[0], hostileContactBoundingBox[0]['latitude'], hostileContactBoundingBox[0]['longitude'])
    side.add_reference_point('蓝方', zone[1], hostileContactBoundingBox[1]['latitude'], hostileContactBoundingBox[1]['longitude'])
    side.add_reference_point('蓝方', zone[2], hostileContactBoundingBox[2]['latitude'], hostileContactBoundingBox[2]['longitude'])
    side.add_reference_point('蓝方', zone[3], hostileContactBoundingBox[3]['latitude'], hostileContactBoundingBox[3]['longitude'])

    side.add_mission_patrol('a1_aaw_miss_1', 0, zone)    # 空战巡逻
    a1_aaw_miss = CPatrolMission('T+1_mode', scenario.mozi_server, scenario.situation)
    a1_aaw_miss.strName = 'a1_aaw_miss_1'
    # 取消满足编队规模才能起飞的限制（任务条令）
    a1_aaw_miss.set_flight_size_check('蓝方', 'a1_aaw_miss_1', True)
    a1_aaw_miss.set_one_third_rule('蓝方', 'a1_aaw_miss_1', True)
    a1_aaw_miss.set_opa_check('蓝方', 'a1_aaw_miss_1', False)
    a1_aaw_miss.set_wwr_check('蓝方', 'a1_aaw_miss_1', True)

    missionUnits = {k: v for k, v in airs_dic.items() if ('Top Hatter' in v.strName) or ('Black Ace' in v.strName)}
    a1_aaw_miss.assign_units(missionUnits)
    # for _, v in missionUnits.items():
    #     cmd = "Hs_ScenEdit_SetUnitSensorSwitch({name = '%s', RADER = false})"%(v.strName)
    #     scenario.mozi_server.send_and_recv(cmd)
    cmd = "ScenEdit_SetEMCON('Mission', 'a1_aaw_miss_1', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)

def AttackDoctrineUpdateAirMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    defaultRef = ['AI-AO-1', 'AI-AO-2', 'AI-AO-3', 'AI-AO-4']
    defaults = {v.strName: {'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in side.referencepnts.items()
                if v.strName in defaultRef}
    airContacts_dic = {k: v for k, v in side.contacts.items() if v.m_ContactType == 0}      # 探测到的敌方飞机
    airs_dic = side.aircrafts       # 本方所有飞机
    patrolmssn = [v for _, v in side.patrolmssns.items() if v.strName == 'a1_aaw_miss_1']
    if len(patrolmssn) == 0 or len(airs_dic) == 0:
        return False

    hostileContactBoundingBox = FindBoundingBoxForGivenContacts(airContacts_dic, defaults, 3)
    zone = ['a1_aaw_miss_1_rp_1', 'a1_aaw_miss_1_rp_2', 'a1_aaw_miss_1_rp_3', 'a1_aaw_miss_1_rp_4']

    set_str_1 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[0], hostileContactBoundingBox[0]['latitude'], hostileContactBoundingBox[0]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_1)
    set_str_2 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[1], hostileContactBoundingBox[1]['latitude'], hostileContactBoundingBox[1]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_2)
    set_str_3 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[2], hostileContactBoundingBox[2]['latitude'], hostileContactBoundingBox[2]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_3)
    set_str_4 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[3], hostileContactBoundingBox[3]['latitude'], hostileContactBoundingBox[3]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_4)

# a1_aaew_miss_1
def AttackDoctrineCreateAEWMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    defaultRef = ['a1_aaw_miss_1_rp_1', 'a1_aaw_miss_1_rp_2', 'a1_aaw_miss_1_rp_3', 'a1_aaw_miss_1_rp_4']
    linkedMissionPoints = {v.strName: {'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in side.referencepnts.items()
                if v.strName in defaultRef}
    airContacts_dic = {k: v for k, v in side.contacts.items() if v.m_ContactType == 0}      # 探测到的敌方飞机
    airs_dic = side.aircrafts       # 本方所有飞机
    supportmssn = [v for _, v in side.supportmssns.items() if v.strName == 'a1_aaew_miss_1']
    if len(supportmssn) == 1 or len(linkedMissionPoints) == 0 or len(airs_dic) == 0 or len(airContacts_dic) == 0:
        return False

    linkedMissionCenterPoint = MidPointCoordinate(linkedMissionPoints['a1_aaw_miss_1_rp_1']['latitude'],
                                                  linkedMissionPoints['a1_aaw_miss_1_rp_1']['longitude'],
                                                  linkedMissionPoints['a1_aaw_miss_1_rp_3']['latitude'],
                                                  linkedMissionPoints['a1_aaw_miss_1_rp_3']['longitude'])
    patrolBoundingBox = FindBoundingBoxForGivenLocations([MakeLatLong(linkedMissionCenterPoint['latitude'], linkedMissionCenterPoint['longitude'])], 1.0)
    zone = ['a1_aaew_miss_1_rp_1', 'a1_aaew_miss_1_rp_2', 'a1_aaew_miss_1_rp_3', 'a1_aaew_miss_1_rp_4']
    side.add_reference_point('蓝方', zone[0], patrolBoundingBox[0]['latitude'], patrolBoundingBox[0]['longitude'])
    side.add_reference_point('蓝方', zone[1], patrolBoundingBox[1]['latitude'], patrolBoundingBox[1]['longitude'])
    side.add_reference_point('蓝方', zone[2], patrolBoundingBox[2]['latitude'], patrolBoundingBox[2]['longitude'])
    side.add_reference_point('蓝方', zone[3], patrolBoundingBox[3]['latitude'], patrolBoundingBox[3]['longitude'])

    side.add_mission_support('a1_aaew_miss_1', zone)    # 支援任务
    a1_aaew_miss = CSupportMission('T+1_mode', scenario.mozi_server, scenario.situation)
    a1_aaew_miss.strName = 'a1_aaew_miss_1'
    # 取消满足编队规模才能起飞的限制（任务条令）
    a1_aaew_miss.set_flight_size_check('蓝方', 'a1_aaew_miss_1', True)
    a1_aaew_miss.set_one_third_rule('蓝方', 'a1_aaew_miss_1', False)
    # a1_aaew_miss.set_opa_check('蓝方', 'a1_aaew_miss_1', False)
    # a1_aaew_miss.set_wwr_check('蓝方', 'a1_aaew_miss_1', True)

    missionUnits = {k: v for k, v in airs_dic.items() if ('Golden Hawk' in v.strName) and (int(re.sub('\D', '', v.strName)) <= 2)}
    a1_aaew_miss.assign_units(missionUnits)
    # for _, v in missionUnits.items():
    #     cmd = "Hs_ScenEdit_SetUnitSensorSwitch({name = '%s', RADER = false})"%(v.strName)
    #     scenario.mozi_server.send_and_recv(cmd)
    cmd = "ScenEdit_SetEMCON('Mission', 'a1_aaew_miss_1', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)


def AttackDoctrineUpdateAEWAirMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    defaultRef = ['a1_aaw_miss_1_rp_1', 'a1_aaw_miss_1_rp_2', 'a1_aaw_miss_1_rp_3', 'a1_aaw_miss_1_rp_4']
    linkedMissionPoints = {v.strName: {'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in side.referencepnts.items()
                if v.strName in defaultRef}
    airs_dic = side.aircrafts       # 本方所有飞机
    supportmssn = [v for _, v in side.supportmssns.items() if v.strName == 'a1_aaew_miss_1']
    if len(supportmssn) == 0 or len(linkedMissionPoints) == 0 or len(airs_dic) == 0:
        return False

    linkedMissionCenterPoint = MidPointCoordinate(linkedMissionPoints['a1_aaw_miss_1_rp_1']['latitude'],
                                                  linkedMissionPoints['a1_aaw_miss_1_rp_1']['longitude'],
                                                  linkedMissionPoints['a1_aaw_miss_1_rp_3']['latitude'],
                                                  linkedMissionPoints['a1_aaw_miss_1_rp_3']['longitude'])
    patrolBoundingBox = FindBoundingBoxForGivenLocations([MakeLatLong(linkedMissionCenterPoint['latitude'], linkedMissionCenterPoint['longitude'])], 1.0)
    zone = ['a1_aaew_miss_1_rp_1', 'a1_aaew_miss_1_rp_2', 'a1_aaew_miss_1_rp_3', 'a1_aaew_miss_1_rp_4']

    set_str_1 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[0], patrolBoundingBox[0]['latitude'], patrolBoundingBox[0]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_1)
    set_str_2 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[1], patrolBoundingBox[1]['latitude'], patrolBoundingBox[1]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_2)
    set_str_3 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[2], patrolBoundingBox[2]['latitude'], patrolBoundingBox[2]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_3)
    set_str_4 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', zone[3], patrolBoundingBox[3]['latitude'], patrolBoundingBox[3]['longitude'])
    scenario.mozi_server.send_and_recv(set_str_4)

# saaw_miss
def AttackDoctrineCreateStealthAirMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    airContacts_dic = {k: v for k, v in side.contacts.items() if v.m_ContactType == 0}      # 探测到的敌方飞机
    airs_dic = side.aircrafts       # 本方所有飞机
    linkedMission = [v for _, v in side.patrolmssns.items() if v.strName == 'a1_aaw_miss_1']
    patrolmssn = [v for _, v in side.patrolmssns.items() if v.strName == 'a1_saaw_miss_1']
    if len(patrolmssn) == 1 or len(linkedMission) == 0 or len(airs_dic) == 0 or len(airContacts_dic) == 0:
        return False

    zone = ['a1_aaw_miss_1_rp_1', 'a1_aaw_miss_1_rp_2', 'a1_aaw_miss_1_rp_3', 'a1_aaw_miss_1_rp_4']
    side.add_mission_patrol('a1_saaw_miss_1', 0, zone)    # 空战巡逻
    a1_saaw_miss = CPatrolMission('T+1_mode', scenario.mozi_server, scenario.situation)
    a1_saaw_miss.strName = 'a1_saaw_miss_1'
    # 取消满足编队规模才能起飞的限制（任务条令）
    a1_saaw_miss.set_flight_size_check('蓝方', 'a1_saaw_miss_1', True)
    a1_saaw_miss.set_one_third_rule('蓝方', 'a1_saaw_miss_1', False)
    a1_saaw_miss.set_opa_check('蓝方', 'a1_saaw_miss_1', False)
    a1_saaw_miss.set_wwr_check('蓝方', 'a1_saaw_miss_1', True)

    # TODO 隐身飞机
    missionUnits = {k: v for k, v in airs_dic.items() if ('Blackbird' in v.strName) and (9 <= int(re.sub('\D', '', v.strName)) <= 12)}
    a1_saaw_miss.assign_units(missionUnits)
    # for _, v in missionUnits.items():
    #     cmd = "Hs_ScenEdit_SetUnitSensorSwitch({name = '%s', RADER = false})"%(v.strName)
    #     scenario.mozi_server.send_and_recv(cmd)
    cmd = "ScenEdit_SetEMCON('Mission', 'a1_saaw_miss_1', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)


def AttackDoctrineUpdateStealthAirMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    airs_dic = side.aircrafts  # 本方所有飞机
    linkedMission = [v for _, v in side.patrolmssns.items() if v.strName == 'a1_aaw_miss_1']
    patrolmssn = [v for _, v in side.patrolmssns.items() if v.strName == 'a1_saaw_miss_1']
    if len(patrolmssn) == 0 or len(linkedMission) == 0 or len(airs_dic) == 0:
        return False

# aew_sup_miss
def SupportAEWDoctrineCreateMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    airs_dic = side.aircrafts  # 本方所有飞机
    ships = side.ships  # 本方所有舰船
    stennis = [v for _, v in ships.items() if 'Stennis' in v.strName]
    supportmssn = [v for _, v in side.supportmssns.items() if v.strName == 'aew_sup_miss']
    if len(supportmssn) == 1 or len(airs_dic) == 0 or len(stennis) == 0:
        return False

    patrolBoundingBox = FindBoundingBoxForGivenLocations([MakeLatLong(stennis[0].dLatitude, stennis[0].dLongitude)], 1)
    zone = ['aew_sup_miss_rp_1', 'aew_sup_miss_rp_2', 'aew_sup_miss_rp_3', 'aew_sup_miss_rp_4']
    side.add_reference_point('蓝方', zone[0], patrolBoundingBox[0]['latitude'], patrolBoundingBox[0]['longitude'])
    side.add_reference_point('蓝方', zone[1], patrolBoundingBox[1]['latitude'], patrolBoundingBox[1]['longitude'])
    side.add_reference_point('蓝方', zone[2], patrolBoundingBox[2]['latitude'], patrolBoundingBox[2]['longitude'])
    side.add_reference_point('蓝方', zone[3], patrolBoundingBox[3]['latitude'], patrolBoundingBox[3]['longitude'])

    side.add_mission_support('aew_sup_miss', zone)    # 支援任务
    aew_sup_miss = CSupportMission('T+1_mode', scenario.mozi_server, scenario.situation)
    aew_sup_miss.strName = 'aew_sup_miss'
    # 取消满足编队规模才能起飞的限制（任务条令）
    aew_sup_miss.set_flight_size_check('蓝方', 'aew_sup_miss', True)
    aew_sup_miss.set_one_third_rule('蓝方', 'aew_sup_miss', False)
    # a1_aaew_miss.set_opa_check('蓝方', 'a1_aaew_miss_1', False)
    # a1_aaew_miss.set_wwr_check('蓝方', 'a1_aaew_miss_1', True)

    missionUnits = {k: v for k, v in airs_dic.items() if ('Golden Hawk' in v.strName) and (int(re.sub('\D', '', v.strName)) >= 3)}
    aew_sup_miss.assign_units(missionUnits)
    # for _, v in missionUnits.items():
    #     cmd = "Hs_ScenEdit_SetUnitSensorSwitch({name = '%s', RADER = false})"%(v.strName)
    #     scenario.mozi_server.send_and_recv(cmd)
    cmd = "ScenEdit_SetEMCON('Mission', 'aew_sup_miss', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)

def SupportAEWDoctrineUpdateMissionAction(scenario):
    return False

# aaw_d_miss
def DefendDoctrineCreateAirMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    airs_dic = side.aircrafts  # 本方所有飞机
    ships =  side.ships # 本方所有舰船
    stennis = [v for _, v in ships.items() if 'Stennis' in v.strName]
    patrolmssn = [v for _, v in side.patrolmssns.items() if v.strName == 'a1_aaw_d_miss']
    if len(patrolmssn) == 1 or len(airs_dic) == 0 or len(stennis) == 0:
        return False

    patrolBoundingBox = FindBoundingBoxForGivenLocations([MakeLatLong(stennis[0].dLatitude, stennis[0].dLongitude)], 3)
    zone = ['a1_aaw_d_miss_rp_1', 'a1_aaw_d_miss_rp_2', 'a1_aaw_d_miss_rp_3', 'a1_aaw_d_miss_rp_4']
    side.add_reference_point('蓝方', zone[0], patrolBoundingBox[0]['latitude'], patrolBoundingBox[0]['longitude'])
    side.add_reference_point('蓝方', zone[1], patrolBoundingBox[1]['latitude'], patrolBoundingBox[1]['longitude'])
    side.add_reference_point('蓝方', zone[2], patrolBoundingBox[2]['latitude'], patrolBoundingBox[2]['longitude'])
    side.add_reference_point('蓝方', zone[3], patrolBoundingBox[3]['latitude'], patrolBoundingBox[3]['longitude'])

    side.add_mission_patrol('a1_aaw_d_miss', 0, zone)  # 空战巡逻
    aaw_d_miss = CPatrolMission('T+1_mode', scenario.mozi_server, scenario.situation)
    aaw_d_miss.strName = 'a1_aaw_d_miss'
    # 取消满足编队规模才能起飞的限制（任务条令）
    aaw_d_miss.set_flight_size_check('蓝方', 'a1_aaw_d_miss', False)
    aaw_d_miss.set_one_third_rule('蓝方', 'a1_aaw_d_miss', False)
    aaw_d_miss.set_opa_check('蓝方', 'a1_aaw_d_miss', True)
    aaw_d_miss.set_wwr_check('蓝方', 'a1_aaw_d_miss', True)

    missionUnits = {k: v for k, v in airs_dic.items() if ('Vigalante' in v.strName) and (int(re.sub('\D', '', v.strName)) in (1, 3, 4))}
    aaw_d_miss.assign_units(missionUnits)
    # for _, v in missionUnits.items():
    #     cmd = "Hs_ScenEdit_SetUnitSensorSwitch({name = '%s', RADER = false})"%(v.strName)
    #     scenario.mozi_server.send_and_recv(cmd)
    cmd = "ScenEdit_SetEMCON('Mission', 'a1_aaw_d_miss', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)


def DefendDoctrineUpdateAirMissionAction(scenario):
    return False

# 巡逻区域经纬度的生成
def create_patrol_zone(scenario, aoPoints):
    side = scenario.get_side_by_name('蓝方')
    # 生成大四边形的四个中点
    rp12mid = MidPointCoordinate(aoPoints[0]['latitude'], aoPoints[0]['longitude'], aoPoints[1]['latitude'],
                                 aoPoints[1]['longitude'])
    rp13mid = MidPointCoordinate(aoPoints[0]['latitude'], aoPoints[0]['longitude'], aoPoints[2]['latitude'],
                                 aoPoints[2]['longitude'])
    rp14mid = MidPointCoordinate(aoPoints[0]['latitude'], aoPoints[0]['longitude'], aoPoints[3]['latitude'],
                                 aoPoints[3]['longitude'])
    rp23mid = MidPointCoordinate(aoPoints[1]['latitude'], aoPoints[1]['longitude'], aoPoints[2]['latitude'],
                                 aoPoints[2]['longitude'])
    rp34mid = MidPointCoordinate(aoPoints[2]['latitude'], aoPoints[2]['longitude'], aoPoints[3]['latitude'],
                                 aoPoints[3]['longitude'])
    # 如果是rec巡逻任务1，添加4个参考点：rp1，rp2，rp3，rp4
        # 巡逻任务1
    side.add_reference_point('蓝方', 'rp2', rp12mid['latitude'], rp12mid['longitude'])
    side.add_reference_point('蓝方', 'rp3', rp13mid['latitude'], rp13mid['longitude'])
    side.add_reference_point('蓝方', 'rp4', rp14mid['latitude'], rp14mid['longitude'])
    zone0 = ['AI-AO-1', 'rp2', 'rp3', 'rp4']
    # 巡逻任务2
    side.add_reference_point('蓝方', 'rp5', rp12mid['latitude'], rp12mid['longitude'])
    side.add_reference_point('蓝方', 'rp7', rp23mid['latitude'], rp23mid['longitude'])
    side.add_reference_point('蓝方', 'rp8', rp13mid['latitude'], rp13mid['longitude'])
    zone1 = ['rp5', 'AI-AO-2', 'rp7', 'rp8']

    # 巡逻任务3
    side.add_reference_point('蓝方', 'rp9', rp13mid['latitude'], rp13mid['longitude'])
    side.add_reference_point('蓝方', 'rp10', rp23mid['latitude'], rp23mid['longitude'])
    side.add_reference_point('蓝方', 'rp12', rp34mid['latitude'], rp34mid['longitude'])
    zone2 = ['rp9', 'rp10', 'AI-AO-3', 'rp12']

    # 巡逻任务4
    side.add_reference_point('蓝方', 'rp13', rp14mid['latitude'], rp14mid['longitude'])
    side.add_reference_point('蓝方', 'rp14', rp13mid['latitude'], rp13mid['longitude'])
    side.add_reference_point('蓝方', 'rp15', rp34mid['latitude'], rp34mid['longitude'])
    zone3 = ['rp13', 'rp14', 'rp15', 'AI-AO-4']

    return zone0, zone1, zone2, zone3

def set_patrol_zone(scenario, aoPoints):
    side = scenario.get_side_by_name('蓝方')
    # 生成大四边形的四个中点
    rp12mid = MidPointCoordinate(aoPoints[0]['latitude'], aoPoints[0]['longitude'], aoPoints[1]['latitude'],
                                 aoPoints[1]['longitude'])
    rp13mid = MidPointCoordinate(aoPoints[0]['latitude'], aoPoints[0]['longitude'], aoPoints[2]['latitude'],
                                 aoPoints[2]['longitude'])
    rp14mid = MidPointCoordinate(aoPoints[0]['latitude'], aoPoints[0]['longitude'], aoPoints[3]['latitude'],
                                 aoPoints[3]['longitude'])
    rp23mid = MidPointCoordinate(aoPoints[1]['latitude'], aoPoints[1]['longitude'], aoPoints[2]['latitude'],
                                 aoPoints[2]['longitude'])
    rp34mid = MidPointCoordinate(aoPoints[2]['latitude'], aoPoints[2]['longitude'], aoPoints[3]['latitude'],
                                 aoPoints[3]['longitude'])

    # 巡逻任务1
    cmd1 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp2', rp12mid['latitude'], rp12mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd1)
    cmd2 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp3', rp13mid['latitude'], rp13mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd2)
    cmd3 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp4', rp14mid['latitude'], rp14mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd3)

    # 巡逻任务2
    cmd4 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp5', rp12mid['latitude'], rp12mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd4)
    cmd5 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp7', rp23mid['latitude'], rp23mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd5)
    cmd6 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp8', rp13mid['latitude'], rp13mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd6)

    # 巡逻任务3
    cmd7 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp9', rp13mid['latitude'], rp13mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd7)
    cmd8 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp10', rp23mid['latitude'], rp23mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd8)
    cmd9 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp12', rp34mid['latitude'], rp34mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd9)

    # 巡逻任务4
    cmd10 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp13', rp14mid['latitude'], rp14mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd10)
    cmd11 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp14', rp13mid['latitude'], rp13mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd11)
    cmd12 = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
        '蓝方', 'rp15', rp34mid['latitude'], rp34mid['longitude'])
    scenario.mozi_server.send_and_recv(cmd12)


def ReconDoctrineCreateMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    defaultRef = ['AI-AO-1', 'AI-AO-2', 'AI-AO-3', 'AI-AO-4']
    defaults = {v.strName: {'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in side.referencepnts.items()
                if v.strName in defaultRef}
    key_order = sorted(defaults.keys())
    aoPoints = [defaults[key] for key in key_order]
    airs = side.aircrafts
    recon_airs = {k: v for k, v in airs.items() if 'Blackbird' in v.strName}
    missions = side.get_patrol_missions()
    recon_missions = [mission for mission in missions.values() if 'rec_miss' in mission.strName]

    if len(recon_missions) >= 4 or len(recon_airs) == 0 or len(side.contacts) >= 10 or len(defaults) != 4:
        return False
    zone0, zone1, zone2, zone3 = create_patrol_zone(scenario, aoPoints)
    i = 1
    for zone in [zone0, zone1, zone2, zone3]:
        # 新建巡逻区名字
        patrol_name = 'a1_rec_miss_' + str(i)
        side.add_mission_patrol(patrol_name, 0, zone)
        patrolmssn = CPatrolMission('T+1_mode', scenario.mozi_server, scenario.situation)
        patrolmssn.strName = patrol_name
        patrolmssn.set_flight_size_check('蓝方', patrol_name, False)
        patrolmssn.set_opa_check('蓝方', patrol_name, 'false')
        patrolmssn.set_wwr_check('蓝方', patrol_name, 'true')

        # 设置条令
        # recon_doctrine = patrolmssn.get_doctrine()
        # recon_doctrine.evade_automatically('yes')
        # recon_doctrine.maintain_standoff('yes')
        # recon_doctrine.ignore_emcon_while_under_attack('yes')
        #
        # recon_doctrine.set_weapon_state_for_aircraft('5001')
        # recon_doctrine.set_weapon_state_for_air_group('0')
        # recon_doctrine.dive_on_threat('2')
        # recon_doctrine.set_em_control_status('Radar', 'Passive')

        # 分配飞机给任务
        # recon_airs = [v for _, v in airs.items() if 'Blackbird' in v.strName]
        recon_air = {k: v for k, v in recon_airs.items() if int(re.sub('\D', '', v.strName)) in (i*2-1, i*2)}
        patrolmssn.assign_units(recon_air)
        # for _, v in recon_air.items():
        #     cmd = "Hs_ScenEdit_SetUnitSensorSwitch({name = '%s', RADER = false})" % v.strName
        #     scenario.mozi_server.send_and_recv(cmd)
        cmd = "ScenEdit_SetEMCON('Mission', '%s', 'Radar=Passive')" % patrol_name
        scenario.mozi_server.send_and_recv(cmd)
        i += 1
    return False


def ReconDoctrineUpdateMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    defaultRef = ['AI-AO-1', 'AI-AO-2', 'AI-AO-3', 'AI-AO-4']
    defaults = {v.strName: {'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in side.referencepnts.items()
                if v.strName in defaultRef}
    key_order = sorted(defaults.keys())
    aoPoints = [defaults[key] for key in key_order]
    airs = side.aircrafts
    recon_airs = [v for _, v in airs.items() if 'Blackbird' in v.strName]
    missions = side.get_patrol_missions()
    recon_missions = [mission for mission in missions.values() if 'rec_miss' in mission.strName]

    if len(recon_missions) < 4 or len(recon_airs) == 0 or len(defaults) != 4:
        return False
    set_patrol_zone(scenario, aoPoints)

    return False


def UpdateAIAreaOfOperations(scenario):
    side = scenario.get_side_by_name('蓝方')
    zone = ['AI-AO-1', 'AI-AO-2', 'AI-AO-3', 'AI-AO-4']
    defaults = {v.strName: {'latitude': v.dLatitude, 'longitude': v.dLongitude} for k, v in
                side.referencepnts.items() if v.strName in zone}

    hostileContacts = side.contacts
    inventory = {**side.aircrafts, **side.ships}
    #  Loop and Get Coordinates
    coordinates = []
    for k, v in hostileContacts.items():
        coordinates.append(MakeLatLong(v.dLatitude, v.dLongitude))
    for k, v in inventory.items():
        coordinates.append(MakeLatLong(v.dLatitude, v.dLongitude))
    # Create Defense Bounding Box
    patrolBoundingBox = FindBoundingBoxForGivenLocations(coordinates, 3)

    if len(defaults) < 4:
        # patrolBoundingBox = FindBoundingBoxForGivenLocations(coordinates, 3.0)
        side.add_reference_point('蓝方', zone[0], patrolBoundingBox[0]['latitude'], patrolBoundingBox[0]['longitude'])
        side.add_reference_point('蓝方', zone[1], patrolBoundingBox[1]['latitude'], patrolBoundingBox[1]['longitude'])
        side.add_reference_point('蓝方', zone[2], patrolBoundingBox[2]['latitude'], patrolBoundingBox[2]['longitude'])
        side.add_reference_point('蓝方', zone[3], patrolBoundingBox[3]['latitude'], patrolBoundingBox[3]['longitude'])
    else:
        for i in range(len(patrolBoundingBox)):
            cmd = "ScenEdit_SetReferencePoint({{side='{}',name='{}', lat={}, lon={}}})".format(
                '蓝方', 'AI-AO-' + str(i+1), patrolBoundingBox[i]['latitude'], patrolBoundingBox[i]['longitude'])
            scenario.mozi_server.send_and_recv(cmd)

# tan_sup_miss
def SupportTankerDoctrineCreateMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    airs_dic = side.aircrafts  # 本方所有飞机
    ships = side.ships  # 本方所有舰船
    stennis = [v for _, v in ships.items() if 'Chung-Hoon' in v.strName]
    supportmssn = [v for _, v in side.supportmssns.items() if v.strName == 'aew_sup_miss']
    if len(supportmssn) == 1 or len(airs_dic) == 0 or len(stennis) == 0:
        return False

    patrolBoundingBox = FindBoundingBoxForGivenLocations([MakeLatLong(stennis[0].dLatitude, stennis[0].dLongitude)], 0.5)
    zone = ['tan_sup_miss_rp_1', 'tan_sup_miss_rp_2', 'tan_sup_miss_rp_3', 'tan_sup_miss_rp_4']
    side.add_reference_point('蓝方', zone[0], patrolBoundingBox[0]['latitude'], patrolBoundingBox[0]['longitude'])
    side.add_reference_point('蓝方', zone[1], patrolBoundingBox[1]['latitude'], patrolBoundingBox[1]['longitude'])
    side.add_reference_point('蓝方', zone[2], patrolBoundingBox[2]['latitude'], patrolBoundingBox[2]['longitude'])
    side.add_reference_point('蓝方', zone[3], patrolBoundingBox[3]['latitude'], patrolBoundingBox[3]['longitude'])

    side.add_mission_support('tan_sup_miss', zone)    # 支援任务
    tan_sup_miss = CSupportMission('T+1_mode', scenario.mozi_server, scenario.situation)
    tan_sup_miss.strName = 'tan_sup_miss'
    # 取消满足编队规模才能起飞的限制（任务条令）
    tan_sup_miss.set_flight_size_check('蓝方', 'tan_sup_miss', True)
    tan_sup_miss.set_one_third_rule('蓝方', 'tan_sup_miss', True)
    # a1_aaew_miss.set_opa_check('蓝方', 'a1_aaew_miss_1', False)
    # a1_aaew_miss.set_wwr_check('蓝方', 'a1_aaew_miss_1', True)

    missionUnits = {k: v for k, v in airs_dic.items() if 'Bull' in v.strName}
    tan_sup_miss.assign_units(missionUnits)
    # for _, v in missionUnits.items():
    #     cmd = "Hs_ScenEdit_SetUnitSensorSwitch({name = '%s', RADER = false})"%(v.strName)
    #     scenario.mozi_server.send_and_recv(cmd)
    cmd = "ScenEdit_SetEMCON('Mission', 'tan_sup_miss', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)

    return False

def SupportTankerDoctrineUpdateMissionAction(scenario):
    return False

# asuw_miss
def AttackDoctrineCreateAntiSurfaceShipMissionAction(scenario):
    side = scenario.get_side_by_name('蓝方')
    contacts = side.contacts
    air_contacts = {k: v for k, v in contacts.items() if v.m_ContactType == 0}
    airs_dic = side.aircrafts
    targets = {k: v for k, v in contacts.items() if v.m_ContactType == 2}
    strikemssn = [v for _, v in side.strikemssns.items() if v.strName == 'asuw_miss']
    if len(strikemssn) == 1 or len(airs_dic) == 0 or len(targets) == 0:
        return False

    side.add_mission_strike('asuw_miss', 2)
    asuw_miss = CStrikeMission('T+1_mode', scenario.mozi_server, scenario.situation)
    asuw_miss.strName = 'asuw_miss'
        # 取消满足编队规模才能起飞的限制（任务条令）
    asuw_miss.set_flight_size_check('蓝方', 'asuw_miss', 'false')

    asuw_miss.assign_targets(targets)
    missionUnits = {k: v for k, v in airs_dic.items() if ('Warhawk' in v.strName) or (('Vigalante' in v.strName) and (int(re.sub('\D', '', v.strName)) not in (1, 3, 4)))}
    asuw_miss.assign_units(missionUnits)

    cmd = "ScenEdit_SetEMCON('Mission', 'asuw_miss', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)
    return False

def AttackDoctrineUpdateAntiSurfaceShipMissionAction(scenario):
    return False


def OffensiveConditionalCheck(scenario):
    UpdateAIAreaOfOperations(scenario)
    situationAwareness(scenario)
    # side = scenario.get_side_by_name('蓝方')
    # doctrine = side.get_doctrine()
    cmd = "ScenEdit_SetEMCON('Side', '蓝方', 'Radar=Passive')"
    scenario.mozi_server.send_and_recv(cmd)
    return True

def DefensiveConditionalCheck(scenario):
    return False



























