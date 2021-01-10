# RSS Dashboard

![CodeQL](https://github.com/Colin-XKL/TTRSS-Dashboard/workflows/CodeQL/badge.svg)
![Pylint](https://github.com/Colin-XKL/TTRSS-Dashboard/workflows/Pylint/badge.svg)
![Docker](https://github.com/Colin-XKL/TTRSS-Dashboard/workflows/Docker/badge.svg)

This applicatioion aims to provide some data analysis on your TTRSS.

TTRSS 的一些数据展示与分析,使用`Flask`+`Bootstrap`+`G2Plot`构建

## 主要功能

* TTRSS订阅列表查看
* 针对每个订阅源，可以通过词云的方式查看其日常标题都是哪些方面的内容

## 使用

### Docker方式

#### 命令方式

```shell
sudo docker run -it -p 5000:5000 \
 -e TTRSS_URL=你自己TTRSS的URL \
 -e TTRSS_USER=用户名 \
 -e TTRSS_PASSWORD=密码 \
 --name ttrss-dashboard \
 -d colinxkl/ttrss-dashboard:latest
```

修改对应字段的值，在终端中执行命令，之后访问5000端口即可。

#### Docker-Compose方式

安装了`docker-compose`后，在项目根目录下找到`docker-compose.yml`，修改用户名等字段，执行`docker-compose up -d`即可。访问5000端口即可进行使用。

### 本地搭建环境

#### 1. 配置环境

若使用`pip`  
`pip install -r requirements.txt`  
若使用`pipenv`  
`pipenv install`

#### 2. 配置用户名等信息

若使用环境变量，需要对`TTRSS_URL`  `TTRSS_USER`  `TTRSS_PASSWORD`三个变量进行设置。

也可直接在`getdata.py`的代码中进行修改。

#### 3. 启动

安装完基本环境后，启动flask  
`python3 -m app.py`
会在控制台输出一个url，如 `http://localhost:5000/ `，访问这个地址即可进入主面板

## 反馈

有任何问题或建议欢迎提issue

项目主页：[https://github.com/Colin-XKL/TTRSS-Dashboard](https://github.com/Colin-XKL/TTRSS-Dashboard)

## 协议

MIT
