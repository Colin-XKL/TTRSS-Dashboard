# RSS Dashboard

This applicatioion aims to provide some data analysis on your TTRSS.

TTRSS 的一些数据展示与分析,使用`Flask`+`Bootstrap`+`G2Plot`构建

## 使用

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

## 协议

MIT
