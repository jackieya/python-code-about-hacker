# 运行proxy.py

kali命令行输入命令 `sudo python3 proxy.py 127.0.0.1 8000 www.baidu.com 80 True`

然后浏览器访问`127.0.0.1:8000`即可看到请求的数据包。

![image-20221008164555419](proxy.assets/image-20221008164555419.png)



这里不知道为什么在windows的cmd上相同步骤操作，python会报错：

![image-20221008165139068](proxy.assets/image-20221008165139068.png)

倒腾了半天也不知道是什么原因，知道原因的大佬可以说一下嘛。。。