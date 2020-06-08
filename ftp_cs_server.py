import os
from socket import *
import pickle
import json
server = socket()
#   防止端口被占用
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind(("", 39333))
server.listen(5)
conn, addr = server.accept()

def list_file(user_name):
    print('列出文件目录')
    with os.popen('ls') as cmd:
        lines = cmd.readlines()
    data = pickle.dumps(lines)
    #   print(data)
    res = conn.send(data)
    #   print(f"成功发送{res}字节")


def down(sock, name):
    file_name = name.decode('utf-8')[4:]
    print("下载..." + file_name)
    if os.path.isfile(file_name):
        size = os.stat(file_name).st_size   # 获取文件的字节大小
        print(str(size))
        conn.send(str(size).encode())  # 发送文件大小
        with open(file_name, 'rb')as fr:
            result = fr.read(1024)
            while result:
                sock.send(result)
                result = fr.read(1024)
        print("文件下载完成")
    else:
        print('file error')

    # file_name = name.decode('utf-8')[2:]
    # with open(file_name, 'rb')as fr:
    #     result = fr.read(1024)
    #     while result:
    #         server.send(result)
    #         result = fr.read(1024)
    #     print("发送完毕!")





def upload(sock, data):
    print('上传。。。')
    # 得到文件名长度
    length = int(data.decode('utf-8')[4:7])
    print(length)
    file_name = data.decode('utf-8')[7:7+length]
    print(file_name)
    message = data.decode('utf-8')[7+length:].encode('utf-8')
    # if os.path.isfile(file_name):
    #     print('文件已经存在')
    file_size = int (message)
    print(file_size)
    rece_size = 0
    with open(file_name, 'wb')as fw:
        while rece_size < file_size:
            if file_size - rece_size > 1024:  # 要收不止一次
                size = 1024
            else:  # 最后一次了，剩多少收多少,防止之后发送数据粘包
                size = file_size - rece_size
                print("last receive:", size)
            recv_data = sock.recv(size)
            rece_size += len(recv_data)  # 累加接受数据大小
            fw.write(recv_data)  # 写入文件,

            # if message:
            #     fw.write(message)
            # new_data = sock.recv(1024)
            # while new_data:
            #     fw.write(new_data)
            #     new_data = sock.recv(1024)
    print('上传完成')


def auth():
    print('waitting to accept...')
    print('client: ', addr)
    while True:
        try:
            user_name_bytes = conn.recv(1024)
            user_passwd_bytes = conn.recv(1024)
            user_name = user_name_bytes.decode('utf-8')
            user_passwd = user_passwd_bytes.decode('utf-8')
            with open('user.json', 'r', encoding='utf-8') as f:
                user_dict = json.loads(f.read())
            if user_name in user_dict and user_dict[user_name] == user_passwd:
                conn.send('True'.encode('utf-8'))
                print("ftp连接成功")
                return [user_name,True]
            else:
                conn.send('False'.encode('utf-8'))
        except Exception:
            conn.send('出现问题'.encode('utf-8'))
            return ['',False]


def main():
    print('starting')
    try:
      authres = auth()
      if authres[1]:
          root = os.getcwd()
          user_dir = root + '/' + authres[0]
          os.chdir(user_dir)
          data_sock , addr = server.accept()
      while authres[1]:
          raw_data = conn.recv(1024)
          if raw_data:
                if raw_data.decode('utf-8').startswith('ls'):
                    list_file(authres[0])
                elif raw_data.decode('utf-8').startswith('get'):
                    down(data_sock, raw_data)
                elif raw_data.decode('utf-8').startswith('put'):
                    upload(data_sock, raw_data)
                elif raw_data.decode('utf-8').startswith('abo'):
                    print('退出')
                    conn.close()
                    data_sock.close()
                else:
                    conn.send("错误".encode('utf-8'))
          else:
                continue
    except Exception as e:
        server.close()
        print(e)


if __name__ == '__main__':
    main()

