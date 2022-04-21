# -*- coding: utf-8 -*-
# @Author  : Kimmie, Livy
# @Time    : 2021/8/27 10:37
# @Email   : aishenliwei@163.com
# @FileName: par_sample_file.py
# @Software: PyCharm
# 参数示例文件以及说明

par = '''## parameter files in json format, support python format comments (#)
## It is strongly recommended that all the file path in this file should be absolute path
## which will reduce possible errors (relative path is also supported).
{
    "phases":{
        "begin":{
            "phase":"P",
            "time_offset":-150  ## in seconds, minus number means a few seconds before a phase
        },
        "end":{
            "phase":"P",
            "time_offset":150  ## in seconds, minus number means a few seconds before a phase
        }
    },

    "distance_range": [30, 90],
    "station_path": "stations.csv",
    "events": {        
        "path":"",   ## leave blank(""), and events will be downloaded from neic
        "depth_range":[0, 6371 ], 
        "magnitude_range":[5.5,9.9],
        "time_range":["1997-07-01","2000-01-01"]  ## time format should be "yyyy-mm-dd" 
    },

    ##method to add event information to data(not implimented yet)
    "add_event_head_method":"sac",

    "travel_time_tool":"Taup",   ### Taup or ttimes
    # data_apply_mode: per_station or per_event. 
    # For per_station, data requests will be sent by station, and the file will be arraged by station
    # For per_event, data requests will be sent by event, and the file will be arraged by event
    "data_apply_mode":"per_station",

    #top diretory to store the processed data
    "output_dir":"/media/liuqimin/data/output",  
    
    #top directory contains the input data
    "input_dir":"/media/liuqimin/data/LG_01",    
    
    ##output data format, such as sac, segy, etc.
    "output_data_format":"sac"  
}
'''


breq = '''{
    "prefix":"begin_phase",
    "head":{
        ".NAME":"liuqimin",
        ".INST": "",
        ".MAIL": "",
        ".EMAIL": "breq_fast0@163.com",
        ".PHONE": "",
        ".FAX": "",
        ".MEDIA:": "FTP",
        ".ALTERNATE MEDIA:": "",
        ".ALTERNATE MEDIA:": "",
        ".FROM":"",
        ".QUALITY":"B"
    }
}
'''

email_par = '''{
    "sender":"*********@163.com",
    "receiver":"breq_fast@iris.washington.edu",
    "subject":"breq_fast request",
    "prefix":"begin_phase",
    "head":{
        ".NAME":"livy",
        ".INST": "",
        ".MAIL": "",
        ".EMAIL": "email@163.com",
        ".PHONE": "",
        ".FAX": "",
        ".MEDIA:": "FTP",
        ".ALTERNATE MEDIA:": "",
        ".ALTERNATE MEDIA:": "",
        ".FROM":"",
        ".QUALITY":"B"
    }
}
'''

stations = '''network,name,start_time,end_time,latitude,longitude,elevation,components,location_code
XR,ST08,1998-7-15,1999-12-31,31.299345,90.031418,4899,BHE BHN BHZ,
XR,ST09,1997-7-19,1999-12-31,31.421249,90.004425,4745,BHE BHN BHZ,
XR,NASE,1998-8-7,1999-12-31,31.988605,91.705673,4653,BHE BHN BHZ,
XR,ST19,1998-7-10,1999-12-31,32.057594,89.191223,4596,BHE BHN BHZ,
XR,ST19A,1998-7-24,1999-12-31,32.103352,89.194839,4540,BHE BHN BHZ,
XR,ST36,1998-7-11,1999-12-31,33.521645,88.601639,5070,BHE BHN BHZ,
XR,ST39,1998-7-12,1999-12-31,33.763725,88.400108,5077,BHE BHN BHZ,
'''