#!/usr/bin/env python3

import sys
import requests
from requests.cookies import RequestsCookieJar
from lxml import etree

import time
import random

USERNAME = ''
PASSWORD = ''

def main():
	# Random delay
	print('Randomly delaying 1-300 seconds...')
	time.sleep(random.randint(1,300))

	# Check username and password
	global USERNAME, PASSWORD
	if not USERNAME:	USERNAME = input('请输入学号：')
	if not PASSWORD:	PASSWORD = input('请输入密码：')

	# Prepare for the session
	req = requests.Session()
	cookie_jar = RequestsCookieJar()
	login_payload = {
		'username': USERNAME,
		'password': PASSWORD,
		'service': 'https://weixine.ustc.edu.cn/2020/caslogin'
	}
	url = 'https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin'

	# Login start
	print('Requesting for cookies from: %s' % url)
	r = req.post(url, data=login_payload, allow_redirects=False)

	# Redirections
	while r.status_code in range(300, 304):
		new_location = r.headers['Location']
		print('Redirecting to %s' % new_location)
		cookie_jar.update(r.cookies)
		r = req.get(new_location, allow_redirects=False)

	# Finally update my cookies
	cookie_jar.update(r.cookies)
	# print(cookie_jar.keys())

	# Get my token for later commit
	login_form_data = etree.HTML(r.text)
	token_line = login_form_data.xpath("//*[@id='daliy-report']/form/input/@value")
	assert(len(token_line) == 1)
	token = token_line[0]

	# Close login request
	r.close()

	# Prepare for report request
	headers = { 
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
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
		'now_address' : '1',			# 当前所在地：内地
		'gps_now_address': '',			#
		'now_province': '340000',		# 当前所在地：安徽
		'gps_province': '',				#
		'now_city': '340100',			# 当前所在地：合肥
		'gps_city': '',					#
		'now_detail': '',				#
		'is_inschool': '6',				# 是否在校：西校区
		'body_condition':	'1',		# 当前身体状况：正常
		'body_condition_detail': '',	# 
		'now_status': '1',				# 当前状态：正常在校园内
		'now_status_detail': '',		#
		'has_fever': '0',				# 当前有无发热症状：无
		'last_touch_sars': '0',			# 有无接触患者：无
		'last_touch_sars_date': '',		#
		'last_touch_sars_detail': '',	#
		'last_touch_hubei': '0',		# 有无接触湖北人员：无
		'last_touch_hubei_date': '',	#
		'last_touch_hubei_detail': '',	#
		'last_cross_hubei': '0',		# 有无在湖北停留或路过：无
		'last_cross_sars_date': '',		#
		'last_cross_sars_detail': '',	#
		'return_dest': '1',				# 返校目的地：合肥校本部
		'return_dest_detail': '',		#
		'other_detail': '',				# 其他情况说明：（无）
	}
	print(report_payload)

	# Random delay before requesting daily report
	print('Randomly delaying 10-20 seconds...')
	time.sleep(random.randint(10,20))

	print('=======================')
	# print(cookie_jar.items())
	r = req.post('https://weixine.ustc.edu.cn/2020/daliy_report',
		cookies=cookie_jar, data=report_payload, headers=headers, params=param,
		allow_redirects=False, timeout=50)

	# Redirections
	while r.status_code in range(300, 304):
		new_location = r.headers['Location']
		print('Redirecting to %s' % new_location)
		cookie_jar.update(r.cookies)
		r = req.get(new_location, allow_redirects=False)

	print('Last status code: %d' % r.status_code)
	if (r.status_code == 200):
		ret_text = r.text
		last_report_info_pos = r.text.find('上次上报时间')
		print(ret_text[last_report_info_pos:(last_report_info_pos+26)])
	r.close()

if __name__ == '__main__':
	sys.exit(main())
