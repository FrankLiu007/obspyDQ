### append sys.path first
import sys
import argparse
sys.path.append("../src")
from obspyDQ.DataPool import DataPool

from obspyDQ.utils import station, event
from obspyDQ.utils import common
from obspyDQ import  reftek
from datetime import datetime
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--par", help="location of the parameters file .", required=True)
    args=parser.parse_args()

    # pars_path="par.json"
    pars=common.read_json(args.par)

    pars['events']['time_range'][0]=datetime.strptime(pars['events']['time_range'][0],"%Y-%m-%d")
    pars['events']['time_range'][1]=datetime.strptime(pars['events']['time_range'][1],"%Y-%m-%d")

    stations=station.read(pars['station_path'])
    events=event.read_events(pars['events'])
    pool=DataPool(pars, stations, events)
    all_data=pool.process()
    pool.save("lg.pool")

    result=reftek.fetch_data(pool)

