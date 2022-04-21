#!/usr/bin/python3

import datetime
import pickle

from obspyDQ.utils import event, station, common
from obspyDQ.utils.TravelTime import calculate_travel_time, get_distance


class DataPool:

    def __init__(self, pars, stations, events):
        self.pars=pars
        self.events=events
        self.stations=stations
        self.all_data={}

    def process(self):
        min_mag, max_mag = self.pars["events"]['magnitude_range']
        min_dep, max_dep = self.pars["events"]['depth_range']
        min_dist, max_dist = self.pars['distance_range']
        for sId, station in self.stations.items():
            print("stattion=", station)
            min_time, max_time = station["time_range"]
            for eId, event in self.events.items():
                ##event magnitude
                mag = event["magnitude"]
                if (mag < min_mag or mag > max_mag):
                    continue
                # event depth
                dep = event["depth"]
                if (dep < min_dep or dep > max_dep):
                    continue
                ##event not in station operation period
                if event["time"] < min_time or event["time"] > max_time:
                    continue
                ## distance range
                dist = get_distance(station['latitude'], station['longitude'], event['latitude'], event['longitude'])
                if dist > max_dist or dist < min_dist:
                    continue

                rr = self.processing_one_event(dist, station, event)
                if rr:  # make sure data exists
                    self.all_data[station["id"], event["id"]] = rr
        return self.all_data

    def processing_one_event(self, dist, station, event):
        par = self.pars
        tmin = station['start_time']
        tmax = station['end_time']

        evlo = event['longitude']
        evla = event["latitude"]
        evdep = event['depth']

        stla = station['latitude']
        stlo = station['longitude']

        t1 = event['time']

        time0 = 0
        time1 = 0
        b_phase = par['phases']['begin']['phase']
        b_offset = par['phases']['begin']['time_offset']

        e_phase = par['phases']['end']['phase']
        e_offset = par['phases']['end']['time_offset']
        # "0" stands for the event origin time
        phases = set()
        if b_phase != "0":
            phases.add(b_phase)
        if e_phase != "0":
            phases.add(e_phase)

        arrivals = calculate_travel_time(dist, evdep, phases, par['travel_time_tool'])

        result = []
        t0 = event["time"] + datetime.timedelta(seconds=b_offset)
        if b_phase != "0":
            if not b_phase in arrivals:
                print(station["name"], "event id=" + str(event["id"]), b_phase, "not found!")
                return {}
            t0 += datetime.timedelta(seconds=arrivals[b_phase]["time"])

        t1 = event["time"] + datetime.timedelta(seconds=e_offset)
        if e_phase != "0":
            if not e_phase in arrivals:
                print(station["name"], event["id"], e_phase, "not found!")
                return {}
            t1 += datetime.timedelta(seconds=arrivals[e_phase]["time"])

        return {"phase": phases, "time_range": (t0, t1), "arrivals": arrivals}


    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            return pickle.load(f)
