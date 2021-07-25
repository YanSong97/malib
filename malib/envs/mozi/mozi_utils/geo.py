#!/usr/bin/python
# -*- coding: utf-8 -*-
######################################
# File name : geo.py
# Create date : 2019-10-21 15:40
# Modified date : 2020-04-22 04:28
# Author : liuzy
# Describe : not set
# Email : lzygzh@126.com
######################################

from math import radians, cos, sin, asin, sqrt, degrees, atan2, degrees
#from mozi_utils import pylog
from malib.envs.mozi.mozi_utils import pylog


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
    dic = {"latitude": my_lat, "longitude": my_lon}
    return dic


def get_two_point_distance(lon1, lat1, lon2, lat2):
    """
    获得两点间的距离
    :param lon1: 1点的经度
    :param lat1: 1点的纬度
    :param lon2: 2点的经度
    :param lat2: 2点的纬度
    :return:
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r * 1000


def get_degree(latA, lonA, latB, lonB):
    """
    获得朝向与正北方向的夹角
    :param latA: A点的纬度
    :param lonA: A点的经度
    :param latB: B点的纬度
    :param lonB: B点的经度
    :return:
    """
    radLatA = radians(latA)
    radLonA = radians(lonA)
    radLatB = radians(latB)
    radLonB = radians(lonB)
    dLon = radLonB - radLonA
    y = sin(dLon) * cos(radLatB)
    x = cos(radLatA) * sin(radLatB) - sin(radLatA) * cos(radLatB) * cos(dLon)
    brng = degrees(atan2(y, x))
    brng = (brng + 360) % 360
    return brng
