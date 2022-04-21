"""
    events format:
    {
        "path":"",  ## if blank, events will be downlaoded from neic
        "depth_range":[0, 6371 ], 
        "magnitude_range":[0,9.9],
        "time_range":["2010-01-01","2010-01-02"]
    }
"""
from . import neic
import io


def filter_events(events, evt_par):
    result = {}
    for id, event in events.items():
        if event['magnitude'] > evt_par['magnitude_range'][1] or event['magnitude'] < evt_par['magnitude_range'][0]:
            continue
        if event['time'] > evt_par['time_range'][1] or event['time'] < evt_par['time_range'][0]:
            continue
        if event['depth'] > evt_par['depth_range'][1] or event['depth'] < evt_par['depth_range'][0]:
            continue
        result[id] = event
    return result


def read_events(evt_par):
    events = []
    if evt_par['path'] != '':
        print("event['path'] not set, begin request event from NEIC")
        with open(evt_par['path'], 'r', encoding='utf-8') as f:
            inf = io.StringIO(f.read())
            events = neic.read_csv_events(inf)
            events = filter_events(events, evt_par)
        if not events:
            print("failed reading events from local file!")
            print("start getting events from NEIC through http")
            events = neic.request_events(evt_par)
    else:
        events = neic.request_events(evt_par)

    return events
