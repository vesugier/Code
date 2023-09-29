# B站相关脚本

![run](./refs/run.jpg)

所有变量名/函数名都写的很清楚是什么作用，测试可用，不提供后续服务

> python自身循环/多线程问题，和C系列语言在抢购方面没什么竞争力，可以自己改写语言，方向是socket的连接和多线程，py版本目前几乎没什么提升空间了

## usage

cookie放置同目录cookie文件夹下

```
├─Code
│  │  README.md
│  │  小会.py
│  │  数藏集.py
│  │  查动态.py
│  │  爬数藏图.py
│  │  爬数藏属性.py
│  │  装扮体验卡轰炸.py
│  │
│  └─cookie
│          1.json
│          2.json
│          3.json
```

格式:

```
{"appkey": "xxxx", "accessKey": "xxxx", "cookie": "SESSDATA=xxx; bili_jct=xxxx; DedeUserID=xxxx; DedeUserID__ckMd5=xxxx; sid=xxx"}
```

> 登录器不开源，严格遵守以上格式，accesskey与appkey需对应，官方版可以删除appkey字段

