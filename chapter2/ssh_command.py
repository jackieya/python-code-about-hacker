import paramiko


# 创建ssh_command函数，会向SSH服务器发起连接并执行一条命令，
# Paramiko支持密钥认证来代替密码认证。
# 这里就使用传统的用户名--密码认证方式登录
def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output:
        print("-- Output --")
        for line in output:
            print(line.strip())


if __name__ == '__main__':
    import getpass

    # user = getpass.getuser()
    user = input("Username: ")
    # 调用getpass模块中的getpass函数，这样用户敲击的字符就不会出现在屏幕上。
    password = getpass.getpass()
    ip = input("Enter server IP: ") or '192.168.1.203'
    port = input('Enter port or <CR>: ') or '2222'
    cmd = input('Enter command or <CR>:') or 'id'
    ssh_command(ip, port, user, password, cmd)
