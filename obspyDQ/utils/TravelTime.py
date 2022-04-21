import subprocess
import pexpect
import sys
import json

from haversine import haversine, Unit
from obspy.taup import TauPyModel
model = TauPyModel(model="iasp91")


def calculate_travel_time(dist, evdep, phases, tool):
    if tool.lower() == "taup":
        return travel_time_taup(dist, evdep, phases)
    elif tool.lower() == "ttimes":
        return travel_time_ttimes(phases, evdep, dist)


#####
def get_distance(stla, stlo, evla, evlo):
    station = (float(stla), float(stlo))
    event = (float(evla), float(evlo))
    dist = haversine(station, event)
    degree = float(dist / 111.19)
    return degree


def travel_time_taup(dist, depth, phases):
    arrivals = model.get_travel_times(source_depth_in_km=depth,
                                      distance_in_degree=dist,
                                      phase_list=phases)
    out = {}
    for arr in arrivals:
        out[arr.name] = {"time": arr.time, "rayp": arr.ray_param_sec_degree}

    return out


def travel_time_ttimes(phases, depth, dist):
    child = pexpect.spawn("ttimes")
    child.expect_exact("*")
    for phase in phases:
        child.sendline(phase)
        child.expect_exact("*")
    child.sendline()
    child.expect_exact("Source depth (km):")
    child.sendline(str(depth))
    child.expect_exact("Enter delta:")
    child.sendline(str(dist))
    child.expect_exact("Enter delta:")
    zz = child.before.decode().split('\r\n')
    child.close()

    out = {}
    for line in zz:
        if not "E-0" in line:
            continue
        kk = line[10:].split()
        out[kk[1]] = {"rayp": float(kk[5]), "time": float(kk[2])}

    return out
