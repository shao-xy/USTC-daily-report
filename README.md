# 中国科学技术大学2019新冠病毒自动打卡脚本

此脚本使用统一身份认证接口的打卡网页进行自动打卡。

## 注意与建议
1. 此脚本仅适用于已返校、正常在校园内的健康同学。
2. 此脚本仅用于替代网页点击行为，使用此脚本视为使用者模拟点击操作，作者不对由于使用此脚本而产生的任何后果负责。
3. 请规范化使用脚本，切勿进行非法行动。

## 脚本名称说明
1. `daily-report.py`为模拟点击的脚本。
2. `daily-report-delay.py`为加入了延迟的脚本。此脚本在运行前和模拟第二次点击前分别增加了5分钟和10-20秒的操作延迟。

## Python版本需求
请使用Python3.x版本（作者系统上安装的版本为`3.7.3`）。

运行前请务必安装`requests`和`lxml`包。安装方法（使用pip）
```
$ pip3 install requests lxml
```

## 使用方法
1. 克隆或下载本项目。
2. 手动提交：直接运行此脚本，脚本会提示输入学号和密码。
3. 自动提交：请在代码最前段中将`USERNAME`和`PASSWORD`变量分别修改为学号和密码，再运行此脚本。
4. 作者宿舍在西校区，如需要修改为其它校区可修改`report_payload`字典中`is_inschool`的值。（其中东、南、中、北、西校区和校外的值分别为2、3、4、5、6和0）
5. 可为此脚本创建自启动任务来自动打卡（具体方法请自行搜索）。

注意：脚本没有考虑密码错误的情况。

## 脚本逻辑
1. 对自动打卡的统一身份认证系统界面，提交用户名和密码，并从多次重定向的页面中获取所有Cookies
2. 在已有Cookies的情况下会得到打卡界面。从页面的提交表单中分离出`_token`键值对。
3. 将`_token`和相应选项一并提交。