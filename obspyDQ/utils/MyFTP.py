import os
import ftplib


class myFtp:
    ftp = ftplib.FTP()

    def __init__(self, host, port=21, user='anonymous', passwd=''):
        self.ftp.connect(host, port)
        self.__login(user, passwd)

    def __login(self, user, passwd=''):
        self.ftp.login(user, passwd)
        print(self.ftp.welcome)

    def download_file(self, remote_file, dst_file):  # 下载当个文件
        file_handler = open(dst_file, 'wb')
        print('download remote file: ', remote_file, ' to ', dst_file)
        # self.ftp.retrbinary("RETR %s" % (RemoteFile), file_handler.write)#接收服务器上文件并写入本地文件
        self.ftp.retrbinary('RETR ' + remote_file, file_handler.write)
        file_handler.close()
        return True

    def download_file_tree(self, remote_dir, dst_dir):  # 下载整个目录下的文件
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        self.ftp.cwd(remote_dir)
        remote_names = self.ftp.nlst()
        for file0 in remote_names:
            local = os.path.join(dst_dir, file0)
            if file0.find(".") == -1:
                if not os.path.exists(local):
                    os.makedirs(local)
                self.download_file_tree(file0, local)
            else:
                self.download_file(file0, local)
        self.ftp.cwd("..")
        return

    def close(self):
        self.ftp.quit()

    def download(self):
        pass


if __name__ == "__main__":
    ftp = myFtp(host='ftp.iris.washington.edu')
    ftp.download_file_tree('data', 'pub/userdata/livy')  # 从目标目录下载到本地目录d盘
    ftp.close()
    print("download succeed!")
