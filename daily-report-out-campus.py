#!/usr/bin/env python3

######################################################
# 自动打卡的参数，请在这改

## 必填信息：

# 科大统一认证账号密码
# （明文保存。请勿分享带密码的脚本给他人）
USERNAME = ''
PASSWORD = ''

# 当前状态：
# 1: 正常在校园内
# 2: 正常在家
# 如非这两种情况请手动打卡
NOW_STATUS = '1'

# 2022/03/22更新：校外居住同学这里不需要再写了，因为打卡界面设置了不允许修改
# （虽然提交请求时硬改是可以的^_^）
CAMPUS_NAME = '合肥市内校外'

# 2022/03/30更新：校外居住报备时需要填写具体位置。校内同学可跳过
## 区县选择：只能选择以下四个区之一：包河区、蜀山区、庐阳区、瑶海区
HOME_DIST = ''
#HOME_DIST = '包河区'
HOME_ADDR = ''

# 紧急联系人：姓名、关系、电话
EMERGENCY_CONTACT = ''
EMERGENCY_CONTACT_RELATION = ''
EMERGENCY_CONTACT_PHONE = ''

# 2022/03/22更新：进出校申请需要选择老师审核！！这里的编号是老师在系统里的编号，
# 一般是10位数字，不知道请运行脚本check-advisor-id.py获取。
# 注意：不是老师的工号，不要乱写！！
ADVISOR_ID = ''

# 2022/03/22更新：进出校原因。需要可自行更改。
GETINSCHOOL_REASON = '日常工作学习需要进出校园。'

# 2022/03/22更新：校外同学选择“进出校申请”时同样需要选择进入哪个校区，选择方法相同。
# 2022/03/20更新：必须选择“跨校区目的地”中的一项或多项！
#   所有可选项为：东/西/南/北/中/高新校区、先研院、国金院
# 可在下面提供的默认选项中选择一行去掉注释即可，或自行修改。多行时只有最后一行会生效。
# 注意：修改时请使用英文逗号和引号，在下面的花括号中手动添加或修改校区名
DESTINATION_CAMPUS = {'东校区', '西校区', '高新校区', '先研院'}
#DESTINATION_CAMPUS = {'东校区', '西校区'}
#DESTINATION_CAMPUS = {'高新校区', '先研院'}
#DESTINATION_CAMPUS = {} # 自行填入

# 后面的内容不需要修改。如不能用请提issue
######################################################
import sys
import requests
from requests.cookies import RequestsCookieJar
from lxml import etree

import time
import random

import datetime

import argparse

# Arguments from command line
args = None

dout = lambda line: (args.debug and print(line))
sleep = lambda n: (not args.no_sleep and time.sleep(n))

def parse_args():
	global args
	parser = argparse.ArgumentParser()
	parser.add_argument('-d', '--debug', action='store_true', help='Debug mode: show debug info')
	parser.add_argument('-i', '--no-sleep', action='store_true', help='Debug mode: no sleep')
	return parser.parse_args()

def check_global_input():
	# Check username and password
	global USERNAME, PASSWORD
	if not USERNAME:	USERNAME = input('请输入学号：')
	if not PASSWORD:	PASSWORD = input('请输入密码：')

def visit(req, fn_name, url, cookie_jar, payload=None, headers=None, param=None):
	fn_list = {'get': req.get, 'post': req.post}
	try:
		fn = fn_list[fn_name.lower()]
	except KeyError:
		raise ValueError('Unsupported visit method: %s' % fn_name)

	dout('Requesting %s' % url)
	r = fn(url, cookies=cookie_jar, data=payload, headers=headers, params=param,
		allow_redirects=False, timeout=50)
	# Trace redirections: keep all cookies
	while r.status_code in range(300, 304):
		url = r.headers['Location']
		dout('Redirecting to %s' % url)
		cookie_jar.update(r.cookies)
		r = req.get(url, cookies=cookie_jar, allow_redirects=False, timeout=50)
	
	# Finally update my cookies
	cookie_jar.update(r.cookies)
	return r

def visit_login_page(req, cookie_jar):
	# Get CAS login page
	r = visit(req, 'get',
	'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin',
	cookie_jar)

	# Get CAS token
	login_form_data = etree.HTML(r.text)
	token_line = login_form_data.xpath("//input[@id='CAS_LT']/@value")
	assert(len(token_line) == 1)
	r.close()
	return token_line[0]

def visit_daily_report_page(req, cookie_jar, token):
	global USERNAME, PASSWORD
	login_payload = {
		'username': USERNAME,
		'password': PASSWORD,
		'CAS_LT': token,
		'service': 'https://weixine.ustc.edu.cn/2020/caslogin',
		'button': '',
		'showCode': '',
		'warn': '',
		'model': 'uplogin.jsp'
	}

	dout(login_payload)
	# Login start
	r = visit(req, 'post',
	'https://passport.ustc.edu.cn/login',
	cookie_jar, login_payload)
	# dout(cookie_jar.keys())
	dout('CAS-Token: %s' % token)
	#dout(r.text)
	#return 0

	# Get my token for later commit
	login_form_data = etree.HTML(r.text)
	token_line = login_form_data.xpath("//*[@id='daliy-report']/form/input/@value")
	assert(len(token_line) == 1)
	# Close login request
	r.close()
	return token_line[0]

def commit_daily_report(req, cookie_jar, token):
	dout('=======================')
	# Prepare for report request
	headers = { 
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
	}
	param = {
		# 'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, image/webp,image/apng, */*; q=0.8, application/signed-exchange; v=b3; q=0.9',
		'Accept - Encoding': 'gzip, deflate, br',
		'Accept - Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
		'Cache - Control': 'max-age=0',
		'Content - Type': 'application/x-www-form-urlencoded',
		'Origin': 'https://weixine.ustc.edu.cn',
		'Referer': 'https://weixine.ustc.edu.cn/2020/home',
		'Src - Fetch - Dest': 'document',
		'Src - Fetch - Mode': 'navigate',
		'Src - Fetch - Site': 'same-origin',
		'Src - Fetch - User': '71',
		'Upgrade - Insecure - Requests': '1'
	}
	report_payload = {
		'_token': token,				# 加入上面获得的token
		#'now_address' : '1',			# 当前所在地：内地
		#'gps_now_address': '',			#
		#'now_province': NOW_PROVINCE,		# 当前所在地（省或直辖市）
		#'gps_province': '',				#
		#'now_city': NOW_CITY,			# 当前所在地（地级市）
		#'gps_city': '',					#
		#'now_country': NOW_DISTRICT,			# 当前所在地（区）
		#'gps_country': '',			#
		#'now_detail': '',				#
		#'is_inschool': WHICH_CAMPUS,				# 是否在校：选择对应校区
		'juzhudi': CAMPUS_NAME,		# 当前校区：（中文）
		'city_area':	HOME_DIST,  # 具体位置：区县选择
		'jutiwz':			HOME_ADDR,  # 具体位置：住址
		'body_condition':	'1',		# 当前身体状况：正常
		'body_condition_detail': '',	# 
		'now_status': NOW_STATUS,				# 当前状态：正常在校园内
		'now_status_detail': '',		#
		'has_fever': '0',				# 当前有无发热症状：无
		'last_touch_sars': '0',			# 有无接触患者：无
		'last_touch_sars_date': '',		#
		'last_touch_sars_detail': '',	#
		'is_danger': '0',					# 当日是否到过疫情中高风险地区：无
		'is_goto_danger': '0',			# 14天内是否有疫情中高风险地区旅居史：无
		'jinji_lxr': EMERGENCY_CONTACT,						# 紧急联系人
		'jinji_guanxi': EMERGENCY_CONTACT_RELATION,				# （紧急联系人）与本人关系
		'jiji_mobile': EMERGENCY_CONTACT_PHONE,	# 紧急联系人电话
		'other_detail': '',				# 其他情况说明：（无）
	}
	dout(report_payload)

	r = visit(req, 'post',
	'https://weixine.ustc.edu.cn/2020/daliy_report',
	cookie_jar, report_payload, headers, param)
	# dout(cookie_jar.items())

	dout('Last status code: %d' % r.status_code)
	#dout(r.text)
	if (r.status_code == 200):
		ret_text = r.text
		last_report_info_pos = r.text.find('上次上报时间')
		dout(ret_text[last_report_info_pos:(last_report_info_pos+26)])
		r.close()
		return 0
	else:
		sys.stderr.write('错误！无法完成上报。')
		sys.stderr.flush()
		return -1

def visit_get_into_campus_application_page(req, cookie_jar):
	# Get application page
	r = visit(req, 'get',
	'https://weixine.ustc.edu.cn/2020/stayinout_apply?t=3',
	cookie_jar)

	# Get my token for later commit
	login_form_data = etree.HTML(r.text)
	token_line = login_form_data.xpath("//*[@id='daliy-report']/form/input/@value")
	assert(len(token_line) == 1)
	# Close application request
	r.close()
	return token_line[0]

def commit_get_into_campus_application(req, cookie_jar, token):
	dout('=======================')
	# Prepare for application request
	headers = { 
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
	}
	param = {
		# 'Accept': 'text/html, application/xhtml+xml, application/xml; q=0.9, image/webp,image/apng, */*; q=0.8, application/signed-exchange; v=b3; q=0.9',
		'Accept - Encoding': 'gzip, deflate, br',
		'Accept - Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
		'Cache - Control': 'max-age=0',
		'Content - Type': 'application/x-www-form-urlencoded',
		'Origin': 'https://weixine.ustc.edu.cn',
		'Referer': 'https://weixine.ustc.edu.cn/2020/stayinout_apply?t=3',
		'Src - Fetch - Dest': 'document',
		'Src - Fetch - Mode': 'navigate',
		'Src - Fetch - Site': 'same-origin',
		'Src - Fetch - User': '71',
		'Upgrade - Insecure - Requests': '1'
	}

	# 这里不要尝试改时间了，已经试过了没用
	start = datetime.datetime.today()
	tomorrow = start + datetime.timedelta(days = 1)
	end = datetime.datetime(
		tomorrow.year,
		tomorrow.month,
		tomorrow.day,
		hour=23,
		minute=59,
		second=59
	)
	payload = {
		'_token': token,
		'choose_ds': ADVISOR_ID,
		'start_date': start.strftime('%Y-%m-%d %H:%M:%S'),
		'end_date': end.strftime('%Y-%m-%d %H:%M:%S'),
		'reason': GETINSCHOOL_REASON,
		'return_college[]': DESTINATION_CAMPUS,
		't': 3	# 进出校申请
	}
	# Application start
	r = visit(req, 'post',
	'https://weixine.ustc.edu.cn/2020/stayinout_apply',
	cookie_jar, payload)
	dout('Last status code: %d' % r.status_code)
	if (r.status_code == 200):
		result_page = etree.HTML(r.text)
		applications_box_headers = result_page.xpath("//div[@id='apply-box']/table/thead/tr[2]/th/text()")
		print('\t'.join(applications_box_headers[:2]))
		applications_box_entries = result_page.xpath("//div[@id='apply-box']/table/tbody/tr")
		for i in range(1, len(applications_box_entries) + 1):
			applications_box_entry_period = result_page.xpath("//div[@id='apply-box']/table/tbody/tr[%d]/td[1]/text()" % i)[0]
			applications_box_entry_status = result_page.xpath("//div[@id='apply-box']/table/tbody/tr[%d]/td[2]/nobr/span/text()" % i)[0]
			print(f'{applications_box_entry_period}\t{applications_box_entry_status}')
		r.close()
		return 0
	else:
		sys.stderr.write('错误！无法完成申请。')
		sys.stderr.flush()
		return -1

def main():
	global args
	args = parse_args()

	#check_global_input()

	# Prepare for the session
	req = requests.Session()
	cookie_jar = RequestsCookieJar()

	# Random delay
	dout(args.no_sleep and '(Skip wait)' or 'Randomly delaying 1-300 seconds...')
	sleep(random.randint(1,300))

	token = visit_login_page(req, cookie_jar)
	token = visit_daily_report_page(req, cookie_jar, token)

	# Random delay before requesting daily report
	dout(args.no_sleep and '(Skip wait)' or 'Randomly delaying 10-20 seconds...')
	sleep(random.randint(10,20))

	# Committing daily report
	if commit_daily_report(req, cookie_jar, token) < 0:
		return -1

	# Random delay before visiting outside-campus application page
	dout(args.no_sleep and '(Skip wait)' or 'Randomly delaying 10-20 seconds...')
	sleep(random.randint(10,20))

	# Visiting outside-campus application page: behave more like a real person
	# Actually this is useless
	visit(req, 'get',
	'https://weixine.ustc.edu.cn/2020/apply/daliy',
	cookie_jar)

	# Random delay before committing cross-campus application
	dout(args.no_sleep and '(Skip wait)' or 'Randomly delaying 10-20 seconds...')
	sleep(random.randint(10,20))

	token = visit_get_into_campus_application_page(req, cookie_jar)

	# Random delay before committing cross-campus application
	dout(args.no_sleep and '(Skip wait)' or 'Randomly delaying 10-20 seconds...')
	sleep(random.randint(10,20))

	return commit_get_into_campus_application(req, cookie_jar, token)

if __name__ == '__main__':
	sys.exit(main())
