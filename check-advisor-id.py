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

def check_advisor_id(req, cookie_jar):
	r = visit(req, 'get',
	'https://weixine.ustc.edu.cn/2020/stayinout_apply?t=3',
	cookie_jar)

	result_page = etree.HTML(r.text)
	advisors_ids = result_page.xpath("//select[@id='choose_ds']/option/@value")
	advisors_names = result_page.xpath("//select[@id='choose_ds']/option/text()")
	for entry in zip(advisors_ids, advisors_names):
		print('\t'.join(entry))

def main():
	global args
	args = parse_args()

	check_global_input()

	# Prepare for the session
	req = requests.Session()
	cookie_jar = RequestsCookieJar()

	token = visit_login_page(req, cookie_jar)
	token = visit_daily_report_page(req, cookie_jar, token)

	return check_advisor_id(req, cookie_jar)

if __name__ == '__main__':
	sys.exit(main())
