#coding=utf-8
import os,sys
import time
sys.path.append('../')
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.filesystems import  AbstractedFS
from server import users, settings



class MyHandler(FTPHandler):
    #每当客户端有一个新的文件传输完成，开始监测服务器的目录下的文件
    def on_file_received(self, file):
        print('received a file: ' + file)
        FTPHandler.on_file_received(self, file)
        #更新服务器下的文件
        file_monitor()

class MyFtpServer(object):
    def __init__(self):
        pass

    def create_server(self):

        self.handler = MyHandler
        self.handler.max_login_attempts = 5 # 在断开连接前最多尝试5次
        self.handler.passive_ports = settings.passive_ports
        self.handler.authorizer = self.authorizer#用户

        self.server = FTPServer((settings.ip, settings.port), self.handler)#设置服务器的ip地址，端口号，handler
        self.server.max_cons = settings.max_cons
        self.server.max_cons_per_ip = settings.max_per_ip
        self.server.serve_forever()

    def listdir(self):
        abstractedfs = AbstractedFS(users.dir, self.handler)

    def create_all_users(self):
        self.authorizer = DummyAuthorizer()
        for user in users.user:
            self.authorizer.add_user(user['name'], user['password'], user['dir'], user['authority'])

def file_monitor():
    if os.path.isdir(users.dir) is True:
        os.chdir(users.dir)
        print(users.dir + ' is existed!')
        files = os.listdir(users.dir)
        now_time = time.time()
        print(now_time)
        for file in files:
            c_time = os.path.getctime(file)
            if (now_time - c_time) > 60*60*24*5:
                #todo 删除文件file
                os.remove(file)
                print('delete file named ' + file)
    else:
        print(users.dir + ' is not existed!')

if __name__ == '__main__':
    ftpserver = MyFtpServer()
    ftpserver.create_all_users()
    ftpserver.create_server()

