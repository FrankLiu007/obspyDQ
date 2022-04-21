import csv
import datetime


def read(path):
    stations = {}
    with open(path, 'r', encoding='utf-8') as inf:
        for index, station in enumerate(csv.DictReader(inf)):
            station['id'] = index
            t0 = datetime.datetime.strptime(station['start_time'], '%Y-%m-%d')
            t1 = datetime.datetime.strptime(station['end_time'], '%Y-%m-%d')
            station["time_range"] = [t0, t1]
            stations[index] = station

    return stations
