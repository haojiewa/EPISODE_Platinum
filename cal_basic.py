#/usr/bin/env python
#coding=utf-8
import re
import time

def chkValidIP(ip):
	pattern = r"\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
	if re.match(pattern, ip):
		return True
	else:
		print 'Invaild IP, please check!'
		return False

def timeStamp():
	return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
