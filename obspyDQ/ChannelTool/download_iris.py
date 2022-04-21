# -*- coding: utf-8 -*-
# @Author  : Livy
# @Time    : 2021/8/18 17:58
# @FileName: download_iris.py
# @Software: PyCharm
# @Info    : 用于通过邮件方式从iris下载数据
import os

import requests
import xlwt

def get_stations(proxies, network, lat_lon=tuple):
    '''
    根据台网名获取其台站信息
    :param network: 台网名
    :param lat_lon: （north, east, south, west）
    :return:
    '''
    payload = {'network': network,
               'maxlat': lat_lon[0],
               'maxlon': lat_lon[1],
               'minlat': lat_lon[2],
               'minlon': lat_lon[3],
               'matchtimeseries': 'true',
               'matchtimeseries': 'false',
               'level': 'station',
               'format': 'text'}
    url = 'http://service.iris.edu/irisws/fedcatalog/1/query'
    r = requests.get(url, payload, proxies=proxies)
    if r.status_code == 200:
        station_lines = [tuple(item.split('|')) for item in r.text.split('\n') if item[:len(network)] == network]
        # Network | Station | Latitude | Longitude | Elevation | Sitename | StartTime | EndTime
        # XF | DONG | 31.979 | 90.9126 | 4607.0 | INDEPTH - III Station DONG, Tibet | 1998 - 08 - 22T00:00: 00 | 1999 - 05 - 26 T00: 00:00
        data = [{
            'network': station[0],
            'station': station[1],
            'latitude': station[2],
            'longitude': station[3],
            'elevation': station[4],
            'sitename': station[5],
            'start_time': station[6],
            'end_time': station[7]
        } for station in station_lines]
        return data
    else:
        raise ValueError('返回状态错误')



if __name__ == "__main__":
    proxies = {
        "http": "http://127.0.0.1:1082",
        "https": "http://127.0.0.1:1082"
    }
    network_list = ['XF', 'XR']
    lat_lon = ['38.4637', '101.0743', '25.6415', '74.2254']
    station_list = []
    for network in network_list:
        stations = get_stations(proxies, network, lat_lon)
        station_list += stations

    # 写入文件
    workbook = xlwt.Workbook(encoding='utf-8')
    worksheet = workbook.add_sheet('station info')
    for index, station in enumerate(station_list):
        worksheet.write(index, 0, station['station'])
        worksheet.write(index, 1, station['network'])
        worksheet.write(index, 2, station['start_time'])
        worksheet.write(index, 3, station['end_time'])

    workbook.save('stations.xlsx')  # 保存文件








