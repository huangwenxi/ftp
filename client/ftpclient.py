#coding=utf-8
from ftplib import FTP
import os
import zipfile
import time
import json
import threading
class FileType(enumerate):
    JA = 0
    JD = 1
    CB = 2

upload_dir = {FileType.JA:'jira-attach', FileType.JD:'jira-db',FileType.CB:'confluence-data'}
class MyftpClient(object):
    def __init__(self):
        self.loadsetting()
        self.ftp = FTP()
        self.ftp.connect(self.config_dict["serverip"], self.config_dict["serverport"])
        self.ftp.login(self.config_dict["user"], self.config_dict["password"])
        self.check_server_dir()

    def loadsetting(self):
        with open("setting.json", "r") as load_f:
            self.config_dict = json.load(load_f)

    #检查当前目录中是否存在dir,不存在则在当前的工作目录创建
    def check_server_dir(self):
        '''Check whether dir exists in the ftp server root directory,
        and does not exists to create in the current directory.'''
        files = self.ftp.nlst()
        if files is None:
            return -1
        for dir in list(upload_dir.values()):
            if dir in files:
                print(dir, '存在')
            else:
                print(dir, '不存在')
                self.ftp.mkd(dir)

    def upload_file(self, path, file):
        '''upload the file to the path directory of thr FTP server.
        path:server storage directory.
        file:file that need to be uploaded.
        '''
        file_handler = open(file.encode(), 'rb')
        self.ftp.storbinary('STOR %s' % os.path.join(path, os.path.basename(file)), file_handler)
        file_handler.close()
        return True

    def delete_file(self, remote_file):
        '''Delet file from the server root directory.
        remote_file:file to be deleted.
        '''
        try:
            self.ftp.delete(remote_file)
        except:
            pass

    def change_direction(self, remote_direction):
        '''Changeing the current working directory of the ftp server'''
        try:
            self.ftp.cwd(remote_direction)
        except Exception as e:
          raise e

    def list_direction(self, remote_direction):
        '''List all the files under the FTP server directory s'''
        try:
            self.change_direction(remote_direction)
            return self.ftp.retrlines('LIST')
        except Exception as e:
            print(e.args)


    def dfs_get_zip_file(self, path, result):
        '''Find all the files in the current system stored in result.
        path:Directory to be found
        result:A dictionary that stores the results
        '''
        if os.path.isdir(path) is False and os.path.isfile(path) is False or result is None:
            print("please check parameter path and result")
            return -1
        files = os.listdir(path)
        for _file in files:
            if os.path.isdir(os.path.join(path, _file)) is True:
                self.dfs_get_zip_file(os.path.join(path, _file), result)
            elif os.path.isfile(os.path.join(path, _file)) is True:
                result.append(os.path.join(path,_file))

    def zip_path(self, input_path, output_name):
        zip_name = output_name
        try:
            f = zipfile.ZipFile(output_name, 'w', compression=zipfile.ZIP_DEFLATED)
            filelists = []
            self.dfs_get_zip_file(input_path, filelists)
            print(filelists)
            for file in filelists:
                print(file)
                f.write(file)
            f.close()
            return zip_name
        except Exception as e:
            print(e.args)

    def process_upload(self, input_path, type):
        # todo 检查服务器中存放Jira和confluence的数据库和附件的数据的目录是否存zai
        """input_path:type:文件的绝对路径
        type:type:文件的类型"""

        if type is FileType.JA:
            zip_name = self.zip_path(input_path, time.ctime(time.time()) + '.zip')
            self.upload_file(upload_dir.get(type), zip_name)
            os.remove(zip_name)
        elif type is FileType.JD:
            files = os.listdir(input_path)
            for _file in files:
                self.upload_file(upload_dir.get(type), os.path.join(input_path, _file))
        elif type is FileType.CB:
            files = os.listdir(input_path)
            for _file in files:
                self.upload_file(upload_dir.get(type), os.path.join(input_path, _file))

    def close(self):
        self.ftp.quit()

def task_timer(ftp_client):
    #todo 判断当前文件夹是否为空，如果不为空则将整个目录上传到服务器,之后删除目录里的文件
    ftp_client.process_upload(ftp_client.config_dict['ja'], FileType.JA)
    ftp_client.process_upload(ftp_client.config_dict['jd'], FileType.JD)
    ftp_client.process_upload(ftp_client.config_dict['cb'], FileType.CB)

    timer = threading.Timer(1, task_timer, [ftp_client])
    timer.start()


if __name__ == '__main__':
    ftp_client = MyftpClient()
    timer = threading.Timer(1, task_timer, [ftp_client])
    timer.start()

    while True:
        time.sleep(60)



