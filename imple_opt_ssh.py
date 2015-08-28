#/usr/bin/env python
#coding=utf-8
import pexpect
import re
import time
import os
import configparser
import logic_main_start as main
import xml.dom.minidom as mdom
import xpath

class eNB_SSH:
	def __init__(self, ip, eType = ''):
		gCfg = main.gCfg
		self.ip = ip
		self.eType = eType
		print ip, eType
		self.status = False
		if self.eType == 'ECCM2':
			self.port = gCfg.ECCM2port
			self.username = gCfg.ECCM2username
			self.password = gCfg.ECCM2password
			self.supassword = gCfg.ECCM2supassword
			self.prompt = gCfg.ECCM2prompt
			self.status = self.login()
		elif self.eType == 'BCAM2':
			self.port = gCfg.BCAM2port
			self.username = gCfg.BCAM2username
			self.password = gCfg.BCAM2password
			self.supassword = gCfg.BCAM2supassword
			self.prompt = gCfg.BCAM2prompt
			self.status = self.login()
		else:
			self.prompt = None
			self.ssh = None

	def __call__(self, cmd):
		return self.cmd(cmd)

	def login(self, ip = None):
		if ip == None:
			ip = self.ip
		signLogin = False
		if self.status:
			self.ssh.sendline('ssh -o StrictHostKeyChecking=no %s@%s' % (self.username, ip))
		else:
			self.ssh = pexpect.spawn('ssh -o StrictHostKeyChecking=no %s@%s' % (self.username, ip), maxread = 99999999)
		arrayScence = [pexpect.TIMEOUT, pexpect.EOF, 'Are you sure you want to continue connecting', 'Host key verification failed.', '[pP]assword:']
		signRst = self.ssh.expect(arrayScence, timeout = 5)
		if signRst == 0:
			print "SSH Login(%s): could not login due to timeout! or cannot match" % ip
		elif signRst == 1:
			if re.search('.*(REMOTE HOST IDENTIFICATION HAS CHANGED!).*', self.ssh.before, re.MULTILINE):
				status = os.system('ssh-keygen -R ' + ip)
				if status == 0:
					signLogin = self.login(ip)
				else:
					print 'ssh-keygen failed!'
			else:
				print ip
		elif signRst == 2:
			# ssh does not have the public key.Just accecpt it.
			self.ssh.sendline('yes')
			signRstL2 = self.ssh.expect([pexpect.TIMEOUT, pexpect.EOF, '[pP]assword:'])
			if signRstL2 == 0:
				print "SSH Login(%s): could not login due to timeout! or cannot match" % ip
			elif signRstL2 == 1:
				print 'ssh-keygen failed!'
			elif signRstL2 == 2:
				self.ssh.sendline(self.password)
				signRstL3 = self.ssh.expect([pexpect.TIMEOUT, pexpect.EOF, self.prompt])
				print 'signRstL3'
				print signRstL3
				if signRstL3 == 0: #timeout
					print "SSH Login(%s): could not login due to timeout! or cannot match" % ip
				elif signRstL3 == 1: #eof
					print 'SSH Login(ip): ' + self.ssh.before
				elif (signRstL3 == 2) and (self.eType == 'ECCM2'): #successfully
					signLogin = True
				elif (signRstL3 == 2) and (self.eType == 'BCAM2'):
					self.ssh.sendline() 
					signRstL4 = self.ssh.expect([pexpect.TIMEOUT, pexpect.EOF, 'Too many connections in \'.*\'\r\r', 'Not enough contexts on server side\r\r', self.prompt])
					if signRstL4 == 4:
						signLogin = True
					elif signRstL4 in range(2,3):
						print 'Too many connections in %s' % ip
						self.ssh.close()
					else:
						self.ssh.close()
		elif signRst == 3:
			if os.system('ssh-keygen -R ' + ip) != 0:
				print ip
				print 'ssh-keygen failed!'
			else:
				self.ssh.close()
				signLogin = self.login(ip)
		elif signRst == 4:
			self.ssh.sendline(self.password) 
			signRstL2 = self.ssh.expect([pexpect.TIMEOUT, pexpect.EOF, self.prompt])
			if signRstL2 == 0: #timeout
				print "SSH Login(%s): could not login due to timeout! or cannot match" % ip
			elif signRstL2 == 1: #eof
				print 'SSH Login(ip): ' + self.ssh.before
			elif (signRstL2 == 2) and (self.eType == 'ECCM2'): #successfully
				signLogin = True
			elif (signRstL2 == 2) and (self.eType == 'BCAM2'):
				self.ssh.sendline() 
				signRstL3 = self.ssh.expect([pexpect.TIMEOUT, pexpect.EOF, 'Too many connections in \'.*\'\r\r', 'Not enough contexts on server side\r\r', self.prompt])
				if signRstL3 == 4:
					signLogin = True
				elif signRstL3 in range(2,3):
					print 'Too many connections in %s' % ip
					self.ssh.close()
				else:
					self.ssh.close()
		return signLogin

	def cmd(self, command, prompt = '', timeout = -1):
		if prompt is '':
			prompt = self.prompt
		time.sleep(1)
		signStatus = True
		self.ssh.sendline(command)
		signRst = self.ssh.expect([prompt, pexpect.TIMEOUT, pexpect.EOF], timeout)
		if signRst == 0:
			resp = self.ssh.before
			resp = resp.replace(command, '').strip()
		elif signRst == 1:
			print ("SSH command:%s cann't execute due to timeout! platform: %s" % (command, self.ip))
			signStatus = False
			resp = self.ssh.before
		elif signRst == 2:
			print ("SSH command:%s cann't execute due to EOF!" % command)
			signStatus = False
			resp = self.ssh.before
		return signStatus, resp

	def exitMode(self):
		self.cmd('exit')
		if self.eType == 'BCAM2':
			self.prompt = main.gCfg.BCAM2prompt
		self.cmd('exit')

	def chgSuMode(self):
		self.prompt = '> \Z'
		self.cmd('sh', '-enb0dev-enb0dev>')
		self.cmd('su', '[pP]assword:')
		self.cmd(self.supassword, '-root-')
		self.cmd('cd /', '-root-/>')

	def loginBB(self, ip):
		self.login(ip)

	def exitBB(self):
		self.exitMode()
		self.cmd('exit', '-root-/>')

if __name__ == '__main__':
	ins = eNB_SSH('10.9.38.16', eType = 'ECCM2')
	ins.chgSuMode()
	ins.login('192.168.2.1')
	ins.chgSuMode()

