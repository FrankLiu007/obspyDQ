import os
import pexpect
import obspy
import numpy as np

from datetime import datetime, timezone, timedelta
import glob
import subprocess

def scan_data_holding(path):
    result=[]
    for day in glob.glob(os.path.join(path,"???????") ):
        d=os.path.split(day)[-1]
        for f in glob.glob(os.path.join(day, '????', '1', '*')) :
            t=os.path.split(f)[-1]
            tt, duration = t.split('_')
            duration=int(duration, 16)
            t0=datetime.strptime(d + tt, "%Y%j%H%M%S%f")
            t1=t0+ timedelta(milliseconds=duration)
            result.append( (f,[t0, t1]) )

    return result

def fetch_data(pool):
 
    in_dir = pool.pars['input_dir']
    out_dir = pool.pars['output_dir']
    out_format = pool.pars['output_data_format']

    ##tempory diretory to store
    pool.pars["tmp_dir"] = "__reftek_temp_dir__"
    if not os.path.exists(pool.pars["tmp_dir"]):
        os.makedirs(pool.pars["tmp_dir"])

    #for key, station in  pool.stations.items():

        ##do not need anymore at present
        #station["local_data_holding"]=scan_data_holding(os.path.join(in_dir, station["network"].strip(), station["name"].strip()))

    for sId, eId in pool.all_data:
        station = pool.stations[sId]
        event = pool.events[eId]
        rr = {}

        stnet = station["network"].strip()
        stnm = station["name"].strip()

        if pool.pars["data_apply_mode"] == "per_station":
            if not os.path.exists(os.path.join(out_dir, stnet, stnm)):
                os.makedirs(os.path.join(out_dir, stnet, stnm))
            out_path = os.path.join(out_dir, stnet, stnm)
        elif pool.pars["data_apply_mode"] == "per_event":
            if not os.path.exists(os.path.join(out_dir, str(eId))):
                os.makedirs(os.path.join(out_dir, str(eId)))
            out_path = os.path.join(out_dir, 'event' + str(eId))
        
        t0=pool.all_data[(sId, eId)]["time_range"][0]
        t1=pool.all_data[(sId, eId)]["time_range"][1]

        tr=fetch_reftek_data(station, pool.pars, t0, t1 )
        if len(tr)==0:  #data not found
            continue

        if out_format.lower().strip() == "sac":

            p=os.path.join(out_path,  station["network"] +"."+ station["name"] + "." + t1.strftime("%Y%j%H%M%S"))
            add_sac_head(tr, station, event)

            ##for masked trace data,  not needed anymore
            # for trace in tr:
            #     if isinstance(trace.data, np.ma.masked_array):
            #         trace.data = trace.data.filled()
            tr.write(p+".sac", format="SAC")
        elif out_format.lower().strip() == "segy":
            pass
        else:
            pass
    return  

def add_sac_head(stream, station, event):

    head={}
    head["kstnm"]=station["name"]
    head["stla"]=station["latitude"]
    head["stlo"]=station["longitude"]
    head["evla"]=event["latitude"]
    head["evlo"]=event["longitude"]
    head["evdp"]=event["depth"]
    head["mag"]=event["magnitude"]

    #for vertical Z component
    head["cmpinc"]=0
    head["kcmpnm"]="Z"
    head["cmpaz"]=0
    stream[0].stats.sac = head
    stream[0].stats.station=station["name"]
    stream[0].stats.network = station["network"]
    stream[0].stats.channel = "Z"

    #for N component
    head["cmpinc"]=90
    head["kcmpnm"]="N"
    head["cmpaz"]=0
    stream[1].stats.sac=head
    stream[0].stats.station = station["name"]
    stream[0].stats.network = station["network"]
    stream[0].stats.channel = "N"

    #for E component
    head["cmpinc"]=90
    head["kcmpnm"]="E"
    head["cmpaz"]=90
    stream[2].stats.sac=head
    stream[0].stats.station = station["name"]
    stream[0].stats.network = station["network"]
    stream[0].stats.channel = "E"

def fetch_reftek_data(station,pars, t0, t1):
    tr = obspy.Stream()

    #clean up the tmp_dir
    for f in glob.glob(os.path.join(pars["tmp_dir"],  "*")):
        os.remove(f)

    in_dir = pars['input_dir']
    out_dir = pars['output_dir']
    out_format = pars['output_data_format']
    out_path=os.path.join(out_dir, station["network"], station["name"])

    t0=t0.strftime('%Y:%j:%H:%M:%S.%f')
    t1=t1.strftime('%Y:%j:%H:%M:%S.%f')
    cmd = "arcfetch " + os.path.join(in_dir, station["network"], station["name"]) + " -C *,*,*," + t0 + "," + t1 + " "+ os.path.join( pars["tmp_dir"],"lqm.rt")

    status, output = subprocess.getstatusoutput(cmd)
    if "No archive error" in output:
        print(cmd)
        print(output)
        print("Please check the data archive have the right archive.sta file. ")
        print('If not, use commond "arcrebuild -Ypass " to rebuild it.')
        exit(1)


    if out_format.lower().strip() == "sac":
        cmd = "pas2sac "+ os.path.join( pars["tmp_dir"],"lqm.rt") +"  "+ pars["tmp_dir"]
        status, output = subprocess.getstatusoutput(cmd)
    elif out_format.lower() == "asc":
        os.system("pas2asc "+os.path.join( pars["tmp_dir"],"lqm.rt") +"  "+ pars["tmp_dir"])
    elif out_format.lower() == "msd":
        os.system("pas2msd "+os.path.join( pars["tmp_dir"],"lqm.rt") + "  "+pars["tmp_dir"])
    elif out_format.lower() == "segy":
        os.system("pas2segy "+ os.path.join( pars["tmp_dir"],"lqm.rt")+ "  " + pars["tmp_dir"])

    for f in glob.glob(os.path.join(pars["tmp_dir"], t0[0:4]+"*")):
        tr+=obspy.read(f)



    return  tr


def fetch_data_by_obspy(t1, t2, station):
    ##failed, due to the obspy do not fully support reftek data
    tr = obspy.Stream()
    file_list=find_match_files(t1,t2, station)

    if not file_list:  ### no file found
        return  tr

    for f in file_list:
        tr+=obspy.read(f,  component_codes=["Z","N","E"])
    tr.merge(method=1, interpolation_samples=0)

    T1=obspy.UTCDateTime(t1.replace(tzinfo=timezone.utc).timestamp() )
    T2=obspy.UTCDateTime(t2.replace(tzinfo=timezone.utc).timestamp() )
    tr.trim(T1, T2)
    return tr

    
def find_match_files(t1,t2, station):
    result=[]
    station["local_data_holding"]
    for path, [tt1, tt2] in station["local_data_holding"]:
        if not (tt2<t1 or t2<tt1):
            result.append(path)
    return result

## add header to sac file
def add_sac_head_by_sac(data):
    sac = pexpect.spawn('sac')
    for item in data:
        sac.expect("SAC>")
        str0 = "read " + item["path"] + "/" + item["time"].strftime("%Y%j%H%M%S") + "*"
        sac.sendline(str0)

        sac.expect("SAC>")
        str0 = "ch " + " evla " + str(item['event']["latitude"]) + \
               " evlo " + str(item['event']["longitude"]) + \
               " evdp " + str(item['event']["depth"])
        sac.sendline(str0)

        sac.expect("SAC>")
        sac.sendline("wh")

    sac.expect("SAC>")
    sac.sendline("q")

    return 0
