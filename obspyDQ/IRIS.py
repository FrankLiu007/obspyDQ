import datetime
import os
import random
from collections import OrderedDict

import requests

from obspyDQ import DataPool
from utils import event, station, common, email

def breq_all_in_one(par_path, breq_par_path, email_par_path="", out_pool_path=""):
    pars = common.read_pars(par_path)
    breq = common.read_json(breq_par_path)
    stations = station.read(pars['station_path'])
    events = event.read_events(pars['events'])
    pool = DataPool.DataPool(pars, stations, events)
    print("Begin calculating all travel time")
    pool.process()

    out_dir = str(datetime.datetime.now())  # output directory for all data
    os.mkdir(out_dir)
    # save the DataPool object  for
    print("saving data pool to local disk")
    if out_pool_path == "":
        out_pool_path = os.path.join(out_dir, "out.pool")
    pool.save(out_pool_path)

    print("Generating breq fast request......")
    reqs = generate_breq_requests(pool, breq)
    print("Sending breq fast request......")

    # ---write out email files----

    for key, value in reqs.items():
        fname = get_label(value)
        with open(os.path.join(out_dir, fname + ".mail"), 'w') as f:
            f.write(value)
    # ----sending emails to ----
    if email_par_path != "":
        email_par = common.read_json(email_par_path)
        for key, value in reqs.items():
            fname = get_label(value)
            print("fname=", fname)
            if email_par:
                email.send_email(email_par, value)

    return pool


def get_label(req):
    for line in req.splitlines():
        if ".LABEL" in line:
            return line.replace(".LABEL", "").strip()


def generate_breq_requests(pool, args_breq_par_path):
    breq = common.read_json(args_breq_par_path)
    requests = OrderedDict()
    breq_head = breq["head"]
    if breq['prefix'] == "begin_phase":
        prefix = pool.pars["phases"]['begin']["phase"]
    elif breq['prefix'] == "end_phase":
        prefix = pool.pars["phases"]['end']["phase"]
    prefix = prefix + '-' + ''.join(random.choices('0123456789', k=4))

    for sId, eId in pool.all_data:
        station = pool.stations[sId]
        # event=pool.events[eId]
        stnet = station["network"]
        stnm = station["name"]
        cmps = station["components"]
        loca = station["location_code"]
        t0 = pool.all_data[(sId, eId)]["time_range"][0]
        t1 = pool.all_data[(sId, eId)]["time_range"][1]

        tmp = stnm + "  " + stnet + "  " + t0.strftime('%Y %m %d %H %M %S.%f') \
              + " " + t1.strftime('%Y %m %d %H %M %S.%f') \
              + " " + str(len(cmps.split())) + " " + cmps + " " + loca
        if pool.pars["data_apply_mode"] == "per_station":
            if sId in requests:
                requests[sId] = requests[sId] + "\n" + tmp
            else:
                breq_head['.LABEL'] = stnet + "." + stnm + "-" + prefix
                head = generate_breq_head(breq_head)
                requests[sId] = head + "\n" + tmp
        elif pool.pars["data_apply_mode"] == "per_event":
            if eId in requests:
                requests[eId] = requests[eId] + "\n" + tmp
            else:
                breq_head['.LABEL'] = "eventId-" + str(eId) + prefix
                head = generate_breq_head(breq_head)
                requests[eId] = head + "\n" + tmp

    return requests


def add_header_by_sac(pool):
    scripts = {}
    for sId, eId in pool.all_data:
        station = pool.stations[sId]
        event = pool.events[eId]

        t0 = pool.all_data[(sId, eId)]["time_range"][0]

        if pool.pars["data_apply_mode"] == "per_station":
            if sId in scripts:
                scripts[sId] = scripts[sId] + get_script(event, station, t0)
            else:
                scripts[sId] = "sac > /dev/null 2>&1 << EOF" + os.linesep
        elif pool.pars["data_apply_mode"] == "per_event":
            if eId in scripts:
                scripts[eId] = scripts[eId] + get_script(event, station, t0)
            else:
                scripts[eId] = "sac > /dev/null 2>&1 << EOF" + os.linesep

    for key, item in scripts.items():
        scripts[key] = scripts[key] + "quit" + os.linesep + "EOF"
    return scripts


#  get_script for one event-station pair
def get_script(event, station, t0):
    # read sac file
    tt = "r *" + station["network"] + "." + station["name"] + "*" + t0.strftime('%Y.%j.%H%M%S') + '*' + os.linesep
    tt = tt + "chnhdr evla " + str(event['latitude']) \
         + " evlo " + str(event['longitude']) \
         + " evdp " + str(event['depth']) \
         + " mag " + str(event['magnitude']) \
         + " stla " + str(station["latitude"]) \
         + " stlo " + str(station["longitude"]) \
         + " stel " + station["elevation"] \
         + " kstnm " + station["name"] \
         + " knetwk " + station["network"] \
         + os.linesep
    tt = tt + 'writehdr' + os.linesep
    return tt


def generate_breq_head(breq_head):
    breq = ""
    for key, value in breq_head.items():
        if value == "":
            continue
        if breq:
            breq = breq + "\n" + key + " " + value
        else:  # 第一个key，不要换行
            breq = key + " " + value
    breq = breq + "\n.END"
    return breq


def update_station(station):
    url0 = "http://ds.iris.edu/mda/" + station["network"] + "/" + station["name"] \
           + "/?starttime=" + station["start_time"] + "&endtime=" + station["end_time"]
    res = requests.get(url0)
    if res.status_code == 204:
        # no stations found
        return []
    elif res.status_code == 200:

        for station in res.text.split('\n'):
            if len(station) < 10:
                continue
            if station[0] == "#":
                continue
            tt = station.split("|")
            stations.append(tt)


def send_emails(reqs, args_email_par):
    email_par = common.read_json(args_email_par)
    if not os.path.exists("emails"):
        os.mkdir("emails")
    for key, value in reqs.items():
        fname = get_label(value)
        print("fname=", fname, '   key=', key)
        email.send_email(email_par, value)
        with open(os.path.join("emails", fname + ".mail"), 'w') as f:
            f.write(value)