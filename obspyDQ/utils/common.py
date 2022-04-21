# -*- coding: utf-8 -*-
# @Author  : Kimmie, Livy
# @Time    : 2021/8/27 10:37
# @Email   : aishenliwei@163.com
# @FileName: common.py
# @Software: PyCharm

import os
import json
import datetime


def read_json(path):
    tt = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            p = line.find("#")
            if p != -1:
                tt.append(line[:p])
            else:
                tt.append(line)
        return json.loads(''.join(tt))
    raise ValueError("error reading file:" + path)


def read_pars(path):
    pars = read_json(path)
    if pars['events']['time_range'][0]:
        pars['events']['time_range'][0] = datetime.datetime.strptime(pars['events']['time_range'][0], "%Y-%m-%d")
    else:
        pars['events']['time_range'][0] = ''
    if pars['events']['time_range'][1]:
        pars['events']['time_range'][1] = datetime.datetime.strptime(pars['events']['time_range'][1], "%Y-%m-%d")
    else:
        pars['events']['time_range'][1] = datetime.datetime.now
    return pars


def get_par_sample_file(save_path):
    """
    获取参数示例文件
    :param save_path: 保存路径
    :return: par.json、email_par.json、 stations.csv
    """
    from .par_sample_file import par, email_par, stations
    par_path = os.path.join(save_path, 'par.json')
    with open(par_path, 'w', encoding='utf-8') as f:
        f.write(par)

    email_path = os.path.join(save_path, 'email_par.json')
    with open(email_path, 'w', encoding='utf-8') as f:
        f.write(email_par)

    stations_path = os.path.join(save_path, 'stations.csv')
    with open(stations_path, 'w', encoding='utf-8') as f:
        f.write(stations)

    print('参数示例文件生成成功, 目录: ', os.path.abspath(save_path))


def mseed2sac():
    """
    messd转sac格式，同时添加时间信息
    :return:
    """
