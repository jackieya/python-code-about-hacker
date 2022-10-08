import sys
import socket
import threading

HEX_FIlTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]
)

# print(HEX_FIlTER)


#  hexdump()函数提供了实时观察代理内数据流通的方法
def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i + length])
        printable = word.translate(HEX_FIlTER)
        hexa = ''.join([f'{ord(c):02x} ' for c in word])
        hexwidth = length * 3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')

    if show:
        for line in results:
            print(line)
    else:
        return results


# print(hexdump('python rocks\n and proxies roll\n'))

# 接受本地或远程数据。connection是socket对象，用空的bytes变量buffer来接收存储socket对象返回的数据。
def receive_from(connection):
    buffer = b""
    # 设定超时时间为5秒
    connection.settimeout(5)
    try:
        # 通过循环把connection返回的数据都写进buffer中，直到数据读完或者连接超时位置。
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    # 最后把buffer返回给调用方，可能是本地设备，也可能是远程设备
    return buffer


# 下面两个函数 request_handler 和response_handler 用于在代理转发数据包之前，修改一下回复的数据包或请求的数据包。
# 通过修改数据包内容，可以进行fuzz测试(模糊测试)，挖权限校验漏洞等等
def request_handler(buffer):
    # perform packet modification
    return buffer


def response_handler(buffer):
    # perform packet modification
    return buffer


# proxy_handler 函数实现整个代理的大部分逻辑。
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 远程连主机
    remote_socket.connect((remote_host, remote_port))

    # 确认是否先从服务器那边接收一些数据，有的服务器会要求这样做，比如FTP服务器会先发送过来一段欢迎消息。
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # 通过response_handler函数来对先发送过来的数据进行一些处理。
        remote_buffer = response_handler(remote_buffer)
        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)
    # 接下来就是代理处理本地和远程发送消息数据的过程。
    while True:
        # 从客户端读取要发送出去的数据，并将该数据流用hexdump展示出来
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Reveived %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)
            # 发送出去之前用request_handler对数据包进行一些处理
            local_buffer = request_handler(local_buffer)
            # 将数据发送给远程服务器
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        # 接收远程服务器发给本地客户端的数据，并将该数据流用hexdump展示出来
        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            # 发送给本地客户端之前先用resonse_handler对数据包进行一些处理
            remote_buffer = response_handler(remote_buffer)
            # 发给本地客户端
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")
        # 当通信两端都没有任何数据时，关闭两端的socket，退出代理循环。
        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connection.")
            break


# server_loop函数，用来创建和管理连接
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        # %r 格式化输出会将原始格式保留。
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] listening on %s:%d" % (local_host, local_port))
    server.listen(5)

    # 进入循环，每发现一个连接就开启一个线程，将新连接交给proxy_handler函数，由它来给数据流两端发数据。
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)
        # start a thread to talk to the remote host
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()


# 最后就是main函数
def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./ proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == '__main__':
    main()
