#!/usr/bin/env python3

######################################################
# 自动打卡的参数，请在这改

## 必填信息：

# 科大统一认证账号密码
# （明文保存。请勿分享带密码的脚本给他人）
USERNAME = ''
PASSWORD = ''

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

def visit_weekly_apply_page(req, cookie_jar):
	# Get weekly apply page
	r = visit(req, 'get',
	'https://weixine.ustc.edu.cn/2020/apply/daliy',
	cookie_jar)

	# Get apply token
	apply_form_data = etree.HTML(r.text)
	#token_line = apply_form_data.xpath("//input[@name='_token']/@value")
	token_line = apply_form_data.xpath("//*[@id='daliy-report']/form/input/@value")
	assert(len(token_line) == 1)
	r.close()
	return token_line[0]

def commit_weekly_apply(req, cookie_jar, token):
	start = datetime.datetime.today()
	end = start + datetime.timedelta(days = 6)
	apply_payload = {
		'_token': token,
		'start_date': start.strftime('%Y-%m-%d'),
		'end_date': end.strftime('%Y-%m-%d')
	}
	dout(apply_payload)
	# Apply start
	r = visit(req, 'post',
	'https://weixine.ustc.edu.cn/2020/apply/daliy/post',
	cookie_jar, apply_payload)
	dout('Last status code: %d' % r.status_code)
	if (r.status_code == 200):
		ret_text = r.text
		last_apply_info_pos = ret_text.find('报备成功')
		dout(ret_text[last_apply_info_pos:(last_apply_info_pos+15)])
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
	visit_daily_report_page(req, cookie_jar, token)

	# Random delay before requesting weekly apply page
	dout(args.no_sleep and '(Skip wait)' or 'Randomly delaying 10-20 seconds...')
	sleep(random.randint(10,20))

	token = visit_weekly_apply_page(req, cookie_jar)

	# Random delay before requesting weekly apply commit
	dout(args.no_sleep and '(Skip wait)' or 'Randomly delaying 10-20 seconds...')
	sleep(random.randint(10,20))
	
	return commit_weekly_apply(req, cookie_jar, token)

if __name__ == '__main__':
	sys.exit(main())
