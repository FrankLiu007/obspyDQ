# -*- coding: utf-8 -*-
# @Author  : Livy
# @Time    : 2021/5/24 14:31
# @FileName: station_spyder.py
# @Software: PyCharm

import requests
from lxml import etree


def get_mda_page(proxies, network=str, station=str, start_time=str, end_time=str):
    '''
    根据台网名和台站名获取具体的时间段和分量
    :param network: 台网名
    :param station: 台站名
    :param start_time: 开始时间
    :param end_time: 结束时间
    :return: str
    '''
    url = f'http://ds.iris.edu/mda/{network}/{station}/?starttime={start_time}&endtime={end_time}'
    res = requests.get(url, proxies, timeout=60)
    if res.status_code == 200:
        return res.text
    else:
        raise Exception('爬取出现错误：' + res.text)


def get_availability_data(datacenter, network_code, station_code, epoch_starttime, epoch_endtime, proxies):
    url = 'http://ds.iris.edu/mda/availability_data_async/'
    callback_data = '{"datacenter":["' + datacenter + '"],"network_code":["' + network_code + '"],"station_code":["' + \
                    station_code + '"],"epoch_starttime":"' + epoch_starttime + '","epoch_endtime":"' + \
                    epoch_endtime + '","level":"station"}'

    FormData = {"callback_data": callback_data}
    headers = {"X-Requested-With": "XMLHttpRequest"}
    res = requests.post(url=url, headers=headers, data=FormData, proxies=proxies, timeout=60)
    if res.status_code == 200:
        availability = res.json()['availability']
        if availability:
            restriction = availability[0]['restriction']
            if restriction == 'OPEN':
                return 'A'
            elif restriction == 'RESTRICTED':
                return 'R'
            elif restriction == 'PARTIALLY':
                return 'P'
            else:
                raise Exception('状态判断出现错误：' + restriction)
        else:
            return None
    else:
        print(callback_data)
        raise Exception('获取状态出现错误：' + res.text)


def parse_description(desc, proxies):
    '''
    解析站点的描述信息
    :param desc: 站点div元素
    :return:
    '''
    description = {}
    description['network'] = desc.xpath('./dl/dd[1]/a/text()')[0]
    description['station'] = desc.xpath('./dl/dd[2]/a/text()')[0]
    description['site_name'] = desc.xpath('./dl/dd[3]/text()')[0].replace('\n', '').strip()
    description['start'] = desc.xpath('./dl/dd[4]/text()')[0].replace('\n', '').strip()
    description['end'] = desc.xpath('./dl/dd[5]/text()')[0].replace('\n', '').strip()
    description['data_center'] = desc.xpath('./dl/dd[6]/ul/li/span/text()')[0].replace('\n', '').strip()
    description['latitude'] = desc.xpath('./dl/dd[7]/text()')[0].replace('\n', '').strip()
    description['longitude'] = desc.xpath('./dl/dd[8]/text()')[0].replace('\n', '').strip()
    description['elevation'] = desc.xpath('./dl/dd[9]/text()')[0].replace('\n', '').strip()
    # 判断可用状态
    description['data_access_status'] = get_availability_data(description['data_center'], description['network'],
                                                              description['station'], description['start'][:10],
                                                              description['end'][:10], proxies)
    return description


def parse_mda_table(table_mda):
    '''
    解析时间与分量表格
    :param table_mda:
    :return:
    '''
    mda_list = []

    tr_list = table_mda.xpath('./tr')
    mda = {}
    for tr in tr_list:
        class_name = tr.get('class')
        if class_name == "epoch":
            if mda:
                mda_list.append(mda)
            mda = {}
            epoch = tr.xpath('./th/text()')[0]
            mda['epoch'] = [item.strip() for item in epoch.split('\n') if len(item) > 10 and ':' in item]
        elif class_name == "col-labels":
            pass
        elif class_name is None:
            location_code = tr.xpath('./th/a/text()')[0].replace('\n', '').strip()
            mda[location_code] = {}
            warp = tr.xpath('./td/dl/*')
            for item in warp:
                cha_name = item.get('class')
                if cha_name == 'cha-label':
                    device = item.xpath('./text()')[0].replace('\n', '').strip()
                    mda[location_code][device] = []
                elif cha_name == 'cha-list':
                    cha_list = item.xpath('./span')
                    for cha_list_item in cha_list:
                        name = cha_list_item.xpath('./a/text()')[0]
                        hertz = cha_list_item.xpath('./small/text()')[0]
                        mda[location_code][device].append([name, hertz])
                else:
                    raise Exception('解析cha-lable出现错误')
        else:
            raise Exception('解析mda表格出现错误')
    else:
        mda_list.append(mda)

    return mda_list


def reset_data(data):
    re_data = []
    for item in data:
        tmp_data = {}
        tmp_data['description'] = item['description']
        tmp_data['locations'] = {}
        for mda in item['mda_table']:
            # 查找location_code
            for location_code, value in mda.items():
                if location_code == 'epoch':
                    continue
                else:
                    if location_code not in tmp_data['locations'].keys():
                        tmp_data['locations'][location_code] = {}
                    # 查找设备
                    for device_name, cha_list in value.items():
                        if device_name not in tmp_data['locations'][location_code].keys():
                            tmp_data['locations'][location_code][device_name] = {}
                        for cha_name, hertz in cha_list:
                            if hertz not in tmp_data['locations'][location_code][device_name].keys():
                                tmp_data['locations'][location_code][device_name][hertz] = {}
                            if cha_name not in tmp_data['locations'][location_code][device_name][hertz].keys():
                                tmp_data['locations'][location_code][device_name][hertz][cha_name] = {}
                                tmp_data['locations'][location_code][device_name][hertz][cha_name]["time"]=[]
                            tmp_data['locations'][location_code][device_name][hertz][cha_name]["time"].append(mda['epoch'])

        # 分量的时间排序，暂时是排序，也可以考虑给定阈值合并时间段
        # for location_code, device in tmp_data['locations'].items():
        #     for device_name, hertz_list in device.items():
        #         for hertz, cha_list in hertz_list.items():
        #             for cha_name, cha_space in cha_list.items():
        #                 # new_time = []
        #                 # for item in cha_space:
        #                 #     pass
        #                 tmp_data['locations'][location_code][device_name][hertz][cha_name].sort()
        #                 # print(tmp_data['locations'][location_code][device_name][hertz][cha_name])

        re_data.append(tmp_data)
    return re_data


def parse_page(proxies, html_text):
    '''
    解析爬取到的页面
    :param page:
    :return:
    '''
    # with open('XR.html', 'r', encoding='utf-8') as f:
    #     html_text = f.read()
    html = etree.HTML(html_text)
    data = []
    #  获取总体时间段，提取数据
    pages = html.xpath('//div[@id="page-content"]/div[position()>4]')
    if not pages:
        # 时间段内没有检索到数据，或者开始时间大于截至时间
        return None

    for page in pages:
        description = parse_description(page.xpath('./div[1]')[0], proxies)
        mda_table = parse_mda_table(page.xpath('./div[2]/table')[0])
        data.append({'description': description,
                     'mda_table': mda_table})

    # 重新组织合并数据
    re_data = reset_data(data)
    return re_data


def crawl(station, network, start_time='', end_time='', proxies=None):
    page = get_mda_page(proxies, network, station, start_time, end_time)
    data = parse_page(proxies, page)
    return data


if __name__ == '__main__':
    start_time = '1994-01-01'
    end_time = '2023-12-31'
    network = 'XR'
    station = 'ST09'
    network = 'IC'
    station = 'LSA'
    proxies = {
        "http": "http://127.0.0.1:1089",
        "https": "http://127.0.0.1:1089"
    }
    page = get_mda_page(network, station, start_time, end_time, proxies)
    # page = ''
    data = parse_page(page, proxies)
    print(data)
