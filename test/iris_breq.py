import os
import time
import tarfile

from obspy import read
from obspy.io.sac import SACTrace

from SeisDQ.SeisDQ import DataPool
from SeisDQ import IRIS
from utils import common, email


def get_par_sample(sample_path=''):
    common.get_par_sample_file(sample_path)


def generate_request_data(email_path, pool_path):
    """
    从IRIS请求数据
    :return:
    """
    args_par = 'par.json'
    pool = DataPool(args_par)
    print("Begin calculating all travel time")
    all_data = pool.process()

    print("saving data pool to local disk")
    pool_path = os.path.join(pool_path, 'iris.pool')
    pool.save(pool_path)

    print("Generating breq fast request......")
    args_email_par = 'email_par.json'
    reqs = IRIS.generate_breq_requests(pool, args_email_par)

    print("save email")
    if not os.path.exists(email_path):
        os.mkdir(email_path)
    for key, value in reqs.items():
        fname = IRIS.get_label(value)
        print("save fname=", fname, '   key=', key)
        with open(os.path.join("emails", fname + ".mail"), 'w') as f:
            f.write(value)


def send_emails(email_path):
    args_email_par = 'email_par.json'
    email_par = common.read_json(args_email_par)

    email_file_list = [f for f in os.listdir(email_path) if os.path.isfile(os.path.join(email_path, f))]
    for email_file in email_file_list:
        email_file = os.path.join(email_path, email_file)
        with open(email_file, 'r') as mf:
            value = mf.read()
            print(email_file)
            time.sleep(3)
            email.send_email(email_par, value)


def download(ftp_path):
    """
    下载IRIS返回的数据
    :param ftp_path: 邮件返回的ftp地址，eg: ftp://ftp.iris.washington.edu/pub/userdata/livyS
    :return:
    """
    from utils.MyFTP import myFtp

    host = ftp_path[6:29]   # eg: ftp.iris.washington.edu
    user = ftp_path[30:]   # eg: pub/userdata/livyS
    ftp = myFtp(host=host)
    ftp.download_file_tree(user, 'data')  # 从目标目录下载到本地目录d盘
    ftp.close()
    print("ok!")


def unzip_tar_mseed(mseed_path, dst_path):
    """
    解压出mseed数据，tar的数据obspy不能读取
    :param mseed_path: 数据目录
    :param dst_path: 存储目录
    :return:
    """
    mseed_file_list = [f for f in os.listdir(mseed_path) if os.path.isfile(os.path.join(mseed_path, f))]
    for mseed_file in mseed_file_list:
        path = os.path.join(mseed_path, mseed_file)
        azip = tarfile.open(path)
        for member in azip.getmembers():
            if member.isfile() and member.name[-6:] == '.mseed':
                new_name = member.name.replace('/', '__').replace('\\', '__')
                member.name = new_name
                azip.extract(member, dst_path)



def add_event_info(mseed_path, pool_path, sac_path):
    """
    为数据添加事件信息
    :param mseed_path: mseed数据存储文件夹
    :param pool_path: pool文件路径
    :param sac_path: sac文件存储文件夹
    :return:
    """
    if not os.path.exists(sac_path):
        os.mkdir(sac_path)

    pool = DataPool.load(pool_path)
    # 重构all_data数据为字典，优化查找
    data_pool = {}
    for (station_id, event_id), rr in pool.all_data.items():
        station = pool.stations[station_id]
        event = pool.events[event_id]
        start_time = rr['time_range'][0].strftime("%Y-%m-%d %H:%M:%S")

        data_pool[(station['network'], station['name'], start_time)] = event

    # 循环所有数据
    number = 0
    mseed_file_list = [f for f in os.listdir(mseed_path) if os.path.isfile(os.path.join(mseed_path, f))]
    for mseed_file in mseed_file_list:
        path = os.path.join(mseed_path, mseed_file)
        mseed = read(path)
        for index, trace in enumerate(mseed.traces):
            trace_start_time = trace.stats['starttime'].strftime("%Y-%m-%d %H:%M:%S")
            key = (trace.stats['network'], trace.stats['station'], trace_start_time)
            event = data_pool.get(key)
            if event:
                # 创建sac文件
                sac = SACTrace.from_obspy_trace(trace)
                sac.evla = event['latitude']
                sac.evlo = event['longitude']
                sac.evdp = event['depth']
                sac.mag = event['magnitude']
                # 如需更多数据，请自行添加
                # sac.kevnm = event['id']
                # sac.ievtyp = event['type']
                # sac.ievreg = event['place']

                sac_name = os.path.join(sac_path, mseed_file[:-6] + '__' + str(index) + '.sac')
                sac.write(sac_name)
            else:
                number = number + 1
                print('未找到对应事件信息', key)

    print('number---', number)


if __name__ == "__main__":
    # 获取配置示例文件
    sample_path = r'../'
    # get_par_sample(sample_path)

    # 根据事件计算到时，生成iris请求邮件
    # email_path = 'emails'
    # pool_path = './'
    # generate_request_data(email_path, pool_path)

    # 发送邮件
    # send_emails(email_path)

    # 使用ftp下载数据
    # ftp_path = 'ftp://ftp.iris.washington.edu/pub/userdata/livyS'
    # download(ftp_path)

    # 解压下载的mseed数据
    # mseed_path = r'C:\Users\ShenlW\Desktop\20210915_iris_data'
    # dst_path = r'C:\Users\ShenlW\Desktop\20210915_iris_data_extract'
    # unzip_tar_mseed(mseed_path, dst_path)

    # 添加事件信息并转存为sac格式
    # pool_path = 'iris_test_20210827.pool'
    # sac_path = r'data\sac'
    # add_event_info(dst_path, pool_path, sac_path)