# 南七技校健康打卡平台模拟打卡、跨校区报备脚本

此脚本使用统一身份认证接口的打卡网页进行自动打卡、跨校区报备和进出校申请。由于某些原因，本脚本暂不提供过验证码功能。

## 注意与建议
1. 此脚本仅适用于已返校、正常在校园内的健康同学。
2. 此脚本仅用于替代网页点击行为，使用此脚本视为使用者模拟点击操作，作者不对由于使用此脚本而产生的任何后果负责。
3. 请规范化使用脚本，切勿进行非法行动。

## 脚本使用说明
1. 需要Python3环境（见[下文](#Python版本需求)）。
2. `daily-report.py`为仅打卡脚本，适用于无需出校的同学。
3. `daily-report-cross-campus.py`为打卡+跨校区申请的脚本，适用于有“在校可跨校区”权限的同学。
4. `daily-report-out-campus.py`为打卡+进出校申请的脚本，适用于有“在校可跨校区”权限的同学且在校外居住的同学。
5. 脚本默认关闭了调试输出，并开启了自动延迟以模拟更加真实的打卡行为。
6. 脚本采用`-d`参数打开调试输出，`-i`参数控制无延迟的打卡（主要用于调试）。可同时使用，例如`python3 daily-report.py -di`

## Python版本需求
请使用Python3.x版本（作者系统上安装的版本为`3.7.3`）。

运行前请务必安装`requests`和`lxml`包。安装方法（使用pip）
```
$ pip3 install requests lxml
```

## 使用方法
1. 克隆或下载本项目。
2. 请修改脚本头部必需的相关个人信息。（修改后请勿分享给他人以防信息泄漏。）
3. 运行脚本`daily-report`开头的脚本即可打卡或打卡并申请跨校区报备、进出校申请。
4. 可为此脚本创建自启动任务来自动打卡（具体方法请自行搜索），但作者不为此行为负责。

注意：脚本没有考虑密码错误的情况。

## 脚本逻辑
1. 获取自动打卡的统一身份认证系统登录页，从页面的提交表单中分离出CAS-Token键值对。
2. 对自动打卡的统一身份认证系统界面，提交用户名和密码和上面获取到的，并从多次重定向的页面中获取所有Cookies
3. 在已有Cookies的情况下会得到打卡界面。从页面的提交表单中分离出`_token`键值对。
4. 将`_token`和相应选项一并提交。
5. 申请报备的页面分为三次请求，第一个页面（跨校区/进出校/离校申请三合一）逻辑比较复杂（详见`doc/cross-campus.md`文件），但可以跳过（本项目对校内居住同学只关注跨校区报备，其它情况请手动操作！）。带报备的脚本会模拟请求一次第一个页面，然后访问第二个页面（选择出校时间和目的地）分离出`_token`键值对。
6. 带报备的脚本最后会带着`_token`和相应选项一并提交报备。
7. 申请进出校的页面同样为三次请求，但第一个页面比较简单，正常情况下只需要选择进入校内。因此直接重定向到`t=3`的第二个页面。
8. 申请进出校的页面提交时需要选择老师审核，提交的表单中需要老师编号，需要用`check-advisor-id.py`获取。请为每次申请负责！
