import pickle
from socket import *
import sys
import os

client = socket()
dest = ("123.56.117.50", 39333)
client.connect(dest)


def login_auth(sock):
    """用户登录三次认证,输入用户名密码跟服务器账号密码匹配返回True,否则返回False"""
    count = 0
    while count < 3:
        user_name = input("请输入账户: ").strip()
        user_passwd = input("请输入密码: ").strip()
        if user_name and user_passwd:
            sock.send(user_name.encode('utf-8'))
            sock.send(user_passwd.encode('utf-8'))
        else:
            count += 1
            continue
        # time.sleep(10)
        login_res_bytes = sock.recv(1024)
        # print(login_res_bytes)
        # print(login_res_bytes.decode('gbk'))
        login_res = login_res_bytes.decode('utf-8')
        if login_res == 'True':
            return True
        else:
            count += 1
            print('access denied')
            print('剩余次数 %d 次' % (3 - count))
            continue
    else:
        print('尝试次数过多！')
        return False


def list_file(message):
    print('列出文件目录')
    client.send(message.encode('utf-8'))
    res = pickle.loads(client.recv(1024))
    print(res)


def down_file(sock, cmd):
    print("下载文件中..")
    client.send(cmd.encode())  # 发送请求
    server_response = client.recv(1024)
    file_size = int(server_response.decode())
    print(file_size)  # 获取文件大小
    rece_size = 0
    file_name = cmd[4:].strip()
    with open(file_name, "wb") as f:
        while rece_size < file_size:
            if file_size - rece_size > 1024:  # 要收不止一次
                size = 1024
            else:  # 最后一次了，剩多少收多少,防止之后发送数据粘包
                size = file_size - rece_size
                print("last receive:", size)
            recv_data = sock.recv(size)
            rece_size += len(recv_data)  # 累加接受数据大小
            f.write(recv_data)  # 写入文件,即下载
    print('download complete')
    # file_name = message[2:].strip()
    # client.send(f"D:{file_name}".encode("utf-8"))
    # # 将接收数据保存
    # with open(file_name, 'wb') as f:
    #     raw_data = client.recv(1024)
    #     while raw_data:
    #         f.write(raw_data)
    #         raw_data = client.recv(1024)
    #     print('下载完成')


def upload_file(sock, message):
    print("上传文件中..")
    # 获取文件名
    abs_path = message[4:].strip()
    file_name = os.path.basename(abs_path)
    num = '%03d' % len(file_name)
    print('路径：' + abs_path)
    print('文件名：' + file_name)
    file_size = os.path.getsize(abs_path)
    send_message = f'put:{num}{file_name}{file_size}'.encode('utf-8')
    # print(send_message)
    client.send(send_message)
    with open(abs_path, 'rb')as fr:
        result = fr.read(1024)
        while result:
            sock.send(result)
            result = fr.read(1024)
    print('上传完成')


def main():
    auth_res = login_auth(client)
    if auth_res:
        data_sock = socket()
        data_sock.connect(dest)
        while True:
            data = input('请输入要执行的命令')
            data = str(data)
            if data.strip() == "abort":
                print("结束")
                client.send(data.encode('utf-8'))
                client.close()
                data_sock.close()
                break
            if data.startswith('ls'):
                list_file(data)
            elif data.startswith('get'):
                down_file(data_sock, data)
            elif data.startswith('put'):
                upload_file(data_sock, data)
    else:
        print("登录失败，退出程序")
        sys.exit(1)


if __name__ == '__main__':
    main()
