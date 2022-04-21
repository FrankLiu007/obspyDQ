import requests
from io import StringIO
import csv
import datetime
import sys


def request_events(evt):
    if not evt["time_range"][0]:
        print("event start time must specified!")
        sys.exit(-1)

    neic_url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv"
    params = {
        'format': 'csv',  # using csv format
        'starttime': evt['time_range'][0].strftime("%Y-%m-%d"),
        'endtime': evt['time_range'][1].strftime("%Y-%m-%d"),
        'minmagnitude': str(evt['magnitude_range'][0]),
        'maxmagnitude': str(evt['magnitude_range'][1]),
        'mindepth': str(evt['depth_range'][0]),
        'maxdepth': str(evt['depth_range'][1])
    }
    r = requests.get(neic_url, params=params)
    print(r.url)
    if r.status_code != 200:
        raise RuntimeError('获取事件列表请求出现错误')

    return read_csv_events(StringIO(r.text))


def read_csv_events(inf):
    events = {}
    for index, evt in enumerate(csv.DictReader(inf)):
        evt['id'] = index
        evt['time'] = datetime.datetime.strptime(evt['time'], '%Y-%m-%dT%H:%M:%S.%fZ')
        evt['magnitude'] = float(evt.pop('mag'))
        evt['depth'] = float(evt['depth'])
        evt['latitude'] = float(evt['latitude'])
        evt['longitude'] = float(evt['longitude'])
        events[index] = evt

    return events


def main():
    evt = {
        "path": "",  # leave blank if you want to download event from neic
        "depth_range": [0, 6371],
        "magnitude_range": [5, 9.9],
        "time_range": ["2014-01-01", "2014-01-02"],

    }
    events = request_events(evt)
    for event in events:
        print(event['event'])


if __name__ == "__main__":
    main()
