#/usr/bin/env python
#coding=utf-8

import re
import struct
import logic_main_start as main
import imple_opt_snmp as snmp
import imple_opt_ssh as ssh
import cal_basic as bf
import time
import string

class getInfo():
	def __init__(self, ip):
		self.ip = ip
		self._createFuncList()
		if bf.chkValidIP(self.ip):
			self.snmpClient = snmp.eNB_SNMP(self.ip)
			eType = self.snmpCBType()
			self.eType = eType.get('Type')
			if self.eType is None:
				gCfg = main.gCfg
				dbbsc = gCfg.createDBbsc()
				searchPara = [{'Cfg.Debug_IP' : ip}, {'Cfg.Site' : gCfg.labsite}]
				result = dbbsc('query', 'CB.Type', {'$and' : searchPara})
				if result is []:
					pass
				else:
					self.eType = result[0][0]
			else:
				pass
			self.sshClient = ssh.eNB_SSH(self.ip, eType = self.eType)
			if self.sshClient.status:
				self.sshStatus = 'enb0dev'
			else:
				self.sshStatus = 'off'
				print self.eType
				print self.ip
				print 'SSH failed!'
		else:
			self.sshStatus = 'off'
			print 'Wrong IP'

	def __call__(self, info):
		if info in self.snmpFuncList:
			doThis = getattr(self, info)
			return doThis()
		elif info in self.sshSuFuncList:
			if self.sshStatus == 'enb0dev':
				self.sshClient.chgSuMode()
				self.sshStatus = 'su'
			doThis = getattr(self, info)
			return doThis()
		elif info in self.sshEnbFuncList:
			if self.sshStatus == 'su':
				self.sshClient.exitMode()
				self.sshStatus = 'enb0dev'
			doThis = getattr(self, info)
			return doThis()
		else:
			print 'No way to match the method! %s, method: %s, eType: %s' % (self.ip, info, self.eType)
			return None


	def _createFuncList(self):
		self.snmpFuncList = ['snmpResetReason', 'snmpEnbFriendlyName', 'snmpLoadVersionInfo', 'snmpBsLastStartUpTime', 'snmpOamCurrIpAddress', 'snmpBBType', 'snmpCBType', 'snmpSFPAmount', 'snmpRRHVersion']
		self.sshEnbFuncList = ['sshD2UVerInfo', 'sshDBUInfo', 'sshGpsStatusInfo', 'sshCBType', 'sshCBSN', 'sshCBTN', 'sshCBVN', 'sshCcmPCBver', 'sshCcmMirRel', 'sshRrhSN', 'sshRRHInfo', 'sshBBInfo']
		self.sshSuFuncList = ['sshCfg', 'sshFreq', 'sshOamIp', 'sshS1Ip', 'sshUptimeInfo', 'sshCBCpuUsage', 'sshCBMemUsage', 'sshLoadVersionInfo', 'sshRsi', 'ssh2BBInfo']

	def sshBBInfo(self):
		if self.eType[0:4] == 'ECCM':
			bbInfo = {}
			status, resp = self.sshClient('ls /OAM-C/oamctrl')
			cemList = re.findall('.*(CfgMgrBB-\d+).*', resp, re.MULTILINE)
			for cem in cemList:
				status, resp = self.sshClient('/OAM-C/oamctrl/' + cem + '/show')
				if not status:
					continue
				else:
					info = {}
					rst = re.search('.*Serial number:(.*)', resp, re.MULTILINE)
					if rst is not None:
						info.update({'Serial_Number' : rst.group(1).strip()})
					rst = re.search('.*Vendor unit type number:(.*)', resp, re.MULTILINE)
					if rst is not None:
						info.update({'Type_Number' : rst.group(1).strip()})
					rst = re.search('.*Version number:(.*)', resp, re.MULTILINE)
					if rst is not None:
						info.update({'Version_Number' : rst.group(1).strip()})
					if info is not {}:
						bbInfo.update({'BB' + cem[11]: info})
			if bbInfo == {}:
				return None
			else:
				return bbInfo
		elif self.eType == 'BCAM2':
			return None
		else:
			return None

	def sshD2UVerInfo(self):
		if self.eType[0:4] == 'ECCM':
			status, resp = self.sshClient('/pltf/pltf/bdetect/racktype')
			if not status:
				return None
			else:
				rst = re.match('.*type is ?(.*)', resp)
				if not rst:
					return None
				return {'D2U_Version' : rst.group(1)}
		elif self.eType == 'BCAM2':
			status, resp = self.sshClient('ls /')
			if not status:
				return None
			else:
				rst = re.search('>\s*(hral(_\d+)?)\s+.*', resp, re.MULTILINE)
				if not rst:
					return None
				else:
					status, resp = self.sshClient('/' + rst.group(1) + '/pltf/bdetect/racktype/')
					if not status:
						return None
					else:
						rst = re.search('.*type is (.*)', resp)
						if not rst:
							return None
						else:
							return {'D2U_Version' : rst.group(1)}
		else:
			return None
	def sshDBUInfo(self):
		dbuInfo = ''
		if self.eType[0:4] == 'ECCM':
			status, resp = self.sshClient('ls /OAM-C/oamctrl')
			if not status:
				return None
			else:
				dbu = re.search('.*(CfgMgrDBU-\d+).*', resp, re.MULTILINE)
				if not dbu:
					return None
				else:
					status, resp = self.sshClient('/OAM-C/oamctrl/' + dbu.group(1) + '/show')
					if not status:
						return None
					else:
						dbuInfo =  resp
		elif self.eType == 'BCAM2':
			status, resp = self.sshClient('ls /')
			if not status:
				return None
			else:
				rst = re.search('>\s*(OAM-C(_\d+)?).*', resp, re.MULTILINE)
				if not rst:
					return None
				else:
					status, resp = self.sshClient('ls ' + '/' + rst.group(1) + '/oamctrl')
					if not status:
						return None
					else:
						dbu = re.search('.*(CfgMgrDBU-\d+).*', resp, re.MULTILINE) 
						if not dbu:
							return None
						else:
							self.sshClient.ssh.sendline('/' + rst.group(1) + '/oamctrl/' + dbu.group(1) + '/show')
							status, resp = self.sshClient('')
							if not status:
								return None
							else:
								dbuInfo =  resp
		else:
			return None
		if dbuInfo != None:
			info = {}
			rst = re.search('.*Serial number *: *(.*)', dbuInfo, re.MULTILINE)
			if rst is not None:
				info.update({'Serial_Number' : rst.group(1).strip()})
			rst = re.search('.*Vendor unit type *: *(.*)', dbuInfo, re.MULTILINE)
			if rst is not None:
				info.update({'Vendor_Unit_Type' : rst.group(1).strip()})
			rst = re.search('.*Vendor unit family type *: *(.*)', dbuInfo, re.MULTILINE)
			if rst is not None:
				info.update({'Family_Type' : rst.group(1).strip()})
			rst = re.search('.*Vendor unit type number *: *(.*)', dbuInfo, re.MULTILINE)
			if rst is not None:	
				info.update({'Type_Number' : rst.group(1).strip()})
			rst = re.search('.*Version number *:(.*)', dbuInfo, re.MULTILINE)
			if rst is not None:
				info.update({'Version_Number' : rst.group(1).strip()})
			if info is not {}:
				return {'DBU': info}
			else:
				return None
		else:
			return None


	def sshGpsStatusInfo(self):
		if self.eType[0:4] == 'ECCM':
			status, resp = self.sshClient('/pltf/pltf/drvclock/priority')
			if (not status) or (resp.find('P1:') == -1):
				return None
			else:
				rst = re.search('P1: CLOCK_([A-Z_]+)\s*\| CLOCK ([A-Z]+)', resp, re.MULTILINE)
				if not rst:
					return None
				else:
					if 'LOCAL' in rst.group(1):
						return {'GPS_Status' : 'FRE ' + rst.group(2)}
					elif 'EXT' in rst.group(1):
						return {'GPS_Status_Status' : 'EXT ' + rst.group(2)}
					elif 'INT' in rst.group(1):
						return {'GPS_Status' : 'INT ' + rst.group(2)}
				return None
		elif self.eType == 'BCAM2':
			status, resp = self.sshClient('ls /')
			if not status:
				return None
			else:
				rst = re.search('>\s*(hral(_\d+)?)\s+.*', resp, re.MULTILINE)
				if not rst:
					return None
				else:
					status, resp = self.sshClient('/' + rst.group(1) + '/hral/TU-1-1-1/show')
					if not status:
						return None
					else:
						version = re.search('.*status (.*)', resp, re.MULTILINE)
						if not version:
							return None
						else:
							return {'GPS_Status' : version.group(1).strip()}
		else:
			return None

	def sshCcmPCBver(self):
		status, resp = self.sshClient('/pltf/pltf/firm/PCBver')
		if not status:
			return None
		else:
			rst = re.match(".*type is ?:? *(.*)!\n?", resp)
			if not rst:
				rst = re.match(".*type is ?:? *(.*)!?\n?", resp)
				if not rst:
					return None
			return {'CCM_PCB_Ver' : rst.group(1)}

	def sshCcmMirRel(self):
		status, resp = self.sshClient('/pltf/pltf/firm/MirRel')
		if not status:
			return None
		else:
			rst = re.match(".*mir release is: *(.*)!", resp)
			if not rst:
				status, resp = self.sshClient('/pltf/pltf/firm/MirReleaseMirRel')
				rst = re.match(".*mir release is: *(.*)!", resp)
				if not rst:
					return None
			return {'CCM_Mir_Rel' : rst.group(1)}

	def _sshCBInfo(self):
		if self.eType[0:4] == 'ECCM':
			status, resp = self.sshClient('ls /OAM-C/oamctrl')
			if not status:
				return None
			else:
				cbList = re.findall('.*(CfgMgrCB-\d+).*', resp, re.MULTILINE)
				for cb in cbList:
					if not cb:
						return None
					else:
						status, resp = self.sshClient('/OAM-C/oamctrl/' + cb + '/show')
						if not status:
							return None
						else:
							return resp
		elif self.eType == 'BCAM2':
			status, resp = self.sshClient('ls /')
			if not status:
				return None
			else:
				rst = re.search('>\s*(OAM-C(_\d+)?).*', resp, re.MULTILINE)
				if not rst:
					return None
				else:
					status, resp = self.sshClient('ls ' + '/' + rst.group(1) + '/oamctrl')
					if not status:
						return None
					else:
						cb = re.search('.*(CfgMgrCB_LRD-\d+).*', resp, re.MULTILINE) 
						if not cb:
							return None
						else:
							self.sshClient.ssh.sendline('/' + rst.group(1) + '/oamctrl/' + cb.group(1) + '/show')
							status, resp = self.sshClient('')
							if not status:
								return None
							else:
								return resp
		else:
			return None


	def sshCBType(self):
		if not hasattr(self, 'cbInfo'):
			self.cbInfo = self._sshCBInfo()
		if self.cbInfo is not None:
			cbType = re.search('.*ritName:(.*)', self.cbInfo, re.MULTILINE)
			if not cbType:
				return None
			else:
				try:
					return {'Type' : cbType.group(1).strip()}
				except:
					return None
		else:
			return None

	def sshCBSN(self):
		if not hasattr(self, 'cbInfo'):
			self.cbInfo = self._sshCBInfo()
		if self.cbInfo is not None:
			cbSN = re.search('.*Serial number:(.*)', self.cbInfo, re.MULTILINE)
			if not cbSN:
				return None
			else:
				try:
					return {'Serial_Number' : cbSN.group(1).strip()}
				except:
					return None
		else:
			return None

	def sshCBTN(self):
		if not hasattr(self, 'cbInfo'):
			self.cbInfo = self._sshCBInfo()
		if self.cbInfo is not None:
			cbTN = re.search('.*Vendor unit type number:(.*)', self.cbInfo, re.MULTILINE)
			if not cbTN:
				return None
			else:
				try:
					return {'Type_Number' : cbTN.group(1).strip()}
				except:
					return None
		else:
			return None

	def sshCBVN(self):
		if not hasattr(self, 'cbInfo'):
			self.cbInfo = self._sshCBInfo()
		if self.cbInfo is not None:
			cbVN = re.search('.*Version number:(.*)', self.cbInfo, re.MULTILINE)
			if not cbVN:
				return None
			else:
				try:
					return {'Version_Number' : cbVN.group(1).strip()}
				except:
					return None
		else:
			return None

	def sshRRHInfo(self):
		rrhInfoList = {}
		if self.eType[0:4] == 'ECCM':
			status, resp = self.sshClient('ls /OAM-C/oamctrl')
			if not status:
				return ''
			else:
				rrhList = re.findall('.*(CfgMgrRRH-\d+).*', resp, re.MULTILINE)
				for rrh in rrhList:
					rrhInfo = {}
					status, resp = self.sshClient('/OAM-C/oamctrl/' + rrh + '/show')
					if not status:
						continue
					elif re.findall('.*(currentState:ItemState:unlocked\(1\).enabled\(1\))', resp, re.MULTILINE):
						rrhName = re.search('.*(RRH-\d+).*', rrh, re.MULTILINE).group(1).strip()
						rrhInfo['Version'] = re.search('.*ritName: *(.*)', resp, re.MULTILINE).group(1).strip()
						rrhInfo['Hw_Type'] = re.search('.*ritHwType: *(.*)', resp, re.MULTILINE).group(1).strip()
						rrhInfo['Vendor_Unit_Type'] = re.search(".*Vendor unit type: *(.*)", resp,re.MULTILINE).group(1).strip()
						rrhInfo['Vendor_Unit_Family_Type'] = re.search(".*Vendor unit family type: *(.*)", resp,re.MULTILINE).group(1).strip()
						rrhInfo['Vendor_Unit_Type_Number'] = re.search(".*Vendor unit type number: *(.*)", resp,re.MULTILINE).group(1).strip()
						rrhInfo['Date_Of_Manufacture'] = re.search(".*Date of manufacture *: *(.*)", resp,re.MULTILINE).group(1).strip()
						rrhInfo['Serial_Number'] = re.search(".*Serial number: *(.*)", resp,re.MULTILINE).group(1).strip()
						for infoKey in rrhInfo.keys():
							if rrhInfo.get(infoKey) is None:
								rrhInfo.pop(infoKey)
							else:
								continue
						if len(rrhInfo) > 0:
							rrhInfoList.update({rrhName : rrhInfo})
						else:
							continue
				if len(rrhInfoList) > 0:
					return rrhInfoList
				else:
					return None
		elif self.eType == 'BCAM2':
			status, resp = self.sshClient('cd /')
			status, resp = self.sshClient('ls')
			if not status:
				return None
			else:
				rst = re.search('>\s*(OAM-C(_\d+)?).*', resp, re.MULTILINE)
				if not rst:
					return None
				else:
					status, resp = self.sshClient('ls /' + rst.group(1) + '/oamctrl')
					if not status:
						return None
					else:
						rrhList = re.findall('.*(CfgMgrRRH-\d+).*', resp, re.MULTILINE)
						if not rrhList:
							return None
						else:
							for rrh in rrhList:
								rrhInfo = {}
								self.sshClient.ssh.sendline('/' + rst.group(1) +'/oamctrl/' + rrh + '/show')
								status, resp = self.sshClient('')
								if not status:
									return None
								else:
									if re.findall('.*(currentState:ItemState:unlocked\(1\).enabled\(1\)).*', resp, re.MULTILINE):
										rrhName = re.search('.*(RRH-\d+).*', rrh, re.MULTILINE).group(1).strip()
										rrhInfo['Version'] = re.search('.*ritName: *(.*)', resp, re.MULTILINE).group(1).strip()
										rrhInfo['Hw_Type'] = re.search('.*ritHwType: *(.*)', resp, re.MULTILINE).group(1).strip()
										rrhInfo['Vendor_Unit_Type'] = re.search(".*Vendor unit type: *(.*)", resp,re.MULTILINE).group(1).strip()
										rrhInfo['Vendor_Unit_Family_Type'] = re.search(".*Vendor unit family type: *(.*)", resp,re.MULTILINE).group(1).strip()
										rrhInfo['Vendor_Unit_Type_Number'] = re.search(".*Vendor unit type number: *(.*)", resp,re.MULTILINE).group(1).strip()
										rrhInfo['Date_Of_Manufacture'] = re.search(".*Date of manufacture *: *(.*)", resp,re.MULTILINE).group(1).strip()
										rrhInfo['Serial_Number'] = re.search(".*Serial number: *(.*)", resp,re.MULTILINE).group(1).strip()
										for infoKey in rrhInfo.keys():
											if rrhInfo.get(infoKey) is None:
												rrhInfo.pop(infoKey)
											else:
												continue
										if len(rrhInfo) > 0:
											rrhInfoList.update({rrhName : rrhInfo})
										else:
											continue
								if len(rrhInfoList) > 0:
									return rrhInfoList
								else:
									return None
		else:
			return None


	def sshCfg(self):
		ssp = self._sshSpecialSubframePatterns()
		sa = self._sshSubframeAssignment()
		if ssp == '' or sa == '':
			return {'Config' : 'N/A'}
		else:
			return {'Config' : 'Config' + sa + '/' + ssp}

	def _sshSpecialSubframePatterns(self):
		status, resp = self.sshClient('grep specialSubframePatterns /data/db/active/mim/database.xml')
		if not status:
			return ''
		else:
			ssp = re.search('<specialSubframePatterns>ssp([\d])</specialSubframePatterns>', resp, re.MULTILINE)
			if ssp is None:
				return ''
			else:
				return ssp.group(1)

	def _sshSubframeAssignment(self):
		status, resp = self.sshClient('grep subframeAssignment /data/db/active/mim/database.xml')
		if not status:
			return ''
		else:
			sa = re.search('<subframeAssignment>sa([\d])</subframeAssignment>', resp, re.MULTILINE)
			if sa is None:
				return ''
			else:
				return sa.group(1)

	def sshFreq(self):
		status, resp = self.sshClient('grep dlEARFCN /data/db/active/mim/database.xml')
		if not status:
			return {'Frequency' : 'N/A'}
		else:
			freq = re.search('<dlEARFCN>([\d]*)</dlEARFCN>', resp, re.MULTILINE)
		if freq == None:
			return {'Frequency' : 'N/A'}
		else:
			if (not freq.group(1)[:-2] in ['37900', '38350', '38950', '39790']) and (self._sshSubframeAssignment() == '1'):
				return {'Frequency' : freq.group(1) + '?'}
			elif (not freq.group(1)[:-2] in ['38100', '38350', '39200', '40040']) and (self._sshSubframeAssignment() == '2'):
				return {'Frequency' : freq.group(1) + '?'}
			else:
				return {'Frequency' : freq.group(1)}

	def sshOamIp(self):
		ip = self._sshOamIpV4()
		if bf.chkValidIP(ip):
			return {'OAM_IP' : ip}
		elif ip == '':
			ip = self._sshOamIpV6()
			if ip != '':
				return {'OAM_IP' : ip}
			else:
				return None
		else:
			return None

	def sshS1Ip(self):
		ip = self._sshS1IpV4()
		if bf.chkValidIP(ip):
			return {'S1_IP' : ip}
		elif ip == '':
			ip = self._sshS1IpV6()
			if ip != '':
				return {'S1_IP' : ip}
			else:
				return None
		else:
				return None

	def _sshS1IpV4(self):
		if not hasattr(self, 'cbifcfg'):
			self._sshCBIfconfig()
		if not hasattr(self, 'TelecomVlan'):
			self._sshVlanInfo()
		for item in self.cbifcfg:
			if re.search('eth\d\.' + self.TelecomVlan, item):
				rst = re.findall('inet addr:\s*([^\s]*)\s*Bcast:.*', item, re.MULTILINE)
				if len(rst) == 1:
					return rst[0]
				else:
					return ''
		return ''

	def _sshS1IpV6(self):
		if not hasattr(self, 'cbifcfg'):
			self._sshCBIfconfig()
		if not hasattr(self, 'TelecomVlan'):
			self._sshVlanInfo()
		for item in self.cbifcfg:
			print item
			if re.search('eth\d\.' + self.TelecomVlan, item):
				rst = re.findall('inet6 addr:\s*([^\s]*)\s*Scope:.*', item, re.MULTILINE)
				print rst
				if len(rst) == 1:
					return rst[0]
				else:
					return ''
		return ''

	def _sshOamIpV4(self):
		if not hasattr(self, 'cbifcfg'):
			self._sshCBIfconfig()
		if not hasattr(self, 'OamVlan'):
			self._sshVlanInfo()
		for item in self.cbifcfg:
			if re.search('eth\d\.' + self.OamVlan, item):
				rst = re.findall('inet addr:\s*([^\s]*)\s*Bcast:.*', item, re.MULTILINE)
				if len(rst) == 1:
					return rst[0]
				else:
					return ''
		return ''

	def _sshOamIpV6(self):
		if not hasattr(self, 'cbifcfg'):
			self._sshCBIfconfig()
		if not hasattr(self, 'OamVlan'):
			self._sshVlanInfo()
		for item in self.cbifcfg:
			if re.search('eth\d\.' + self.OamVlan, item):
				rst = re.findall('inet6 addr:\s*([^\s]*)\s*Scope:.*', item, re.MULTILINE)
				if len(rst) == 1:
					return rst[0]
				else:
					return ''
		return ''

	def _sshCBIfconfig(self):
		status, resp = self.sshClient('ifconfig')
		self.cbifcfg = resp.split('\r\n\r\n') or ''

	def _sshVlanInfo(self):
		self.OamVlan = ''
		self.TelecomVlan = ''
		status1, resp1 = self.sshClient('grep vLanId /data/db/active/mim/database.xml')
		status2, resp2 = self.sshClient('grep vLanName /data/db/active/mim/database.xml')
		if (not status1) or (not status2):
			return False
		else:
			vlanId = re.findall('<vLanId>([\d]+)</vLanId>', resp1, re.MULTILINE)
			vlanName = re.findall('<vLanName>([\S]+)</vLanName>', resp2, re.MULTILINE)
			if (len(vlanId) == 2) and (len(vlanName) == 2):
				if(re.compile(r'Oam|OAM|oam').search(vlanName[0])) and (vlanName[1][0:7] == 'Telecom'):
					self.OamVlan = vlanId[0]
					self.TelecomVlan = vlanId[1]
				elif(re.compile(r'Oam|OAM|oam').search(vlanName[1])) and (vlanName[0][0:7] == 'Telecom'):
					self.OamVlan = vlanId[1]
					self.TelecomVlan = vlanId[0]
				else:
					return False
			elif (len(vlanId) == 1) and (len(vlanName) == 1):
					if re.compile(r'Oam|OAM|oam').search(vlanName[0]):
						self.OamVlan = vlanId[0]
					elif vlanName[0][0:7] == 'Telecom':	
						self.TelecomVlan = vlanId[0]
					else:
						return False
			else:
				print 'OAM ERROR'
				return False

	def sshUptimeInfo(self):
		status, resp = self.sshClient('uptime')
		rst = {}
		if not status:
			return None
		else:
			uptime = re.match('.*up([^,]*),.*', resp, re.MULTILINE)
			load = re.match('.*load average:.*,.*,(.*)', resp, re.MULTILINE)
			if uptime:
				rst.update({'Uptime' : uptime.group(1).strip()})
			if load:
				rst.update({'Load_Average' : load.group(1).strip()})
			return rst

	def sshCBCpuUsage(self):
		result = self._sshCpuUsage()
		if result:
			return {'CPU_Usage' : result}
		else:
			return None

	def _sshCpuUsage(self):
		busytime1, idletime1 = self._sshCpuState()
		if (busytime1 is None) or (idletime1 is None):
			return False
		time.sleep(5)
		busytime2, idletime2 = self._sshCpuState()
		if (busytime2 is None) or (idletime2 is None):
			return False
		busytime = list(map((lambda x, y: y - x), busytime1, busytime2))
		idletime = list(map((lambda x, y: y - x), idletime1, idletime2))
		cpuUsage = list(map((lambda b, i: '%.2f' % ( b * 100.0 / ( b + i ))), busytime, idletime))
		return string.join(cpuUsage, '/')	

	def ssh2BBInfo(self):
		BBInfoList = {}
		if self.eType[0:4] == 'ECCM':
			BBstatus = self._sshCB2BBPingStatus()
			for bb in BBstatus.keys():
				if BBstatus.get(bb) == 'On':
					BBInfo = {}
					self.sshClient.loginBB('192.168.%s.1' % bb[2])
					self.sshClient.chgSuMode()
					cpuUsage = self._sshCpuUsage()
					memUsage = self._sshMemUsage()
					if cpuUsage:
						BBInfo.update({'CPU_Usage' : cpuUsage})
					else:
						pass
					if memUsage:
						BBInfo.update({'Mem_Usage' : memUsage})
					else:
						pass
					uptime = self.sshUptimeInfo()
					BBInfo.update(uptime)
					BBInfoList.update({bb : BBInfo})
					self.sshClient.exitBB()
			return BBInfoList
		elif self.eType == 'BCAM2':
			pass 

	def _sshCB2BBPingStatus(self):
		BBStatus = {}
		for BNo in range(2,5):
			state, recv = self.sshClient('ping -c 1 -w 1 192.168.%d.1' % BNo)
			if not state:
				continue
			else:
				pingLossRate = re.search('.*, *(\d+)% packet loss.*', recv, re.MULTILINE).group(1).strip()
				aliveBBStatus = (lambda x : bool(int(x, 10)))(pingLossRate)
				if aliveBBStatus:
					BBStatus.update({'BB%d' % BNo : 'Off'})
				else:
					BBStatus.update({'BB%d' % BNo : 'On'})
		return BBStatus

	def _sshCpuState(self):
		state, recv = self.sshClient('cat /proc/stat')
		if not state:
			return None, None
		lineList = recv.split('\n')
		busytime = []
		idletime = []
		for line in lineList:
			if line[0:3] == 'cpu':
				total = 0
				cpuStats = line[5:].split(' ')
				for cpuStat in cpuStats:
					total += int(cpuStat)
				busytime.append(total - int(cpuStats[3]))
				idletime.append(int(cpuStats[3]))
		return busytime, idletime

	def sshCBMemUsage(self):
		result = self._sshMemUsage()
		if int(float(result)) in range(0, 100):
			return {'Mem_Usage' : result}
		elif int(float(result)) == 100:
			return {'Mem_Usage' : result}
		else:
			return None

	def _sshMemUsage(self):
		state, recv = self.sshClient('free')
		if not state:
			return None
		lineList = recv.split('\n')
		used = 0
		free = 100
		for line in lineList:
			if 'Mem:' in line:
				valueList = re.findall('(\d+)', line)
				used = int(valueList[1])
				free = int(valueList[2])
				break
		return '%.2f' % (used * 100.0 / (used + free))

	def sshLoadVersionInfo(self):
		status, resp = self.sshClient('cat /data/cfg/sw.txt')
		if not status:
			return None
		version = re.search('RSW_NAME = .*#FV_ENB_(.*)', resp, re.MULTILINE)
		if not version:
			return None
		else:
			return  {'Load_Version' :  version.group(1).strip()}	

	def sshRsi(self):
		status, resp = self.sshClient('grep rootSequenceIndex /data/db/active/mim/database.xml')
		if not status:
			return None
		else:
			rsi = re.findall('<rootSequenceIndex.*>([\d]*)</rootSequenceIndex>', resp, re.MULTILINE)
			try:
				return {'RSI' :string.join(rsi, '/')}
			except:
				print 'Failed: platform get rsi failed, platform:%s' % self.ip
				return None

	def snmpResetReason(self):
		queryResult = self.snmpClient('get', '1.3.6.1.4.1.637.70.4.1.1.4.0')
		if queryResult is not None:
			return {'Reset_Reason_ID' : queryResult}
		else:
			return None

	def snmpEnbFriendlyName(self):
		queryResult = self.snmpClient('get', '1.3.6.1.4.1.637.70.4.1.4.2.10.0')
		if queryResult is not None:
			return {'eNB_Friendly_Name' : queryResult}
		else:
			return None

	def snmpLoadVersionInfo(self):
		queryResult = self.snmpClient('get', '1.3.6.1.4.1.637.70.4.1.2.3.1.0')
		if queryResult is not None:
			if queryResult is not None:
				infoVer = re.search(r'(?:CONV-TDD_|)((?:LL|LR|TA|TS)\d{4}(?:PRI|))_(D\d{2}[0-9,T]{0,2})_(NONE|\d{7}|E\d{5})$', queryResult)
				return {'Load_Version' : infoVer.group(0)}
			else:
				return None
		else:
			return None

	def snmpBsLastStartUpTime(self):
		queryResult = self.snmpClient('get', '1.3.6.1.4.1.637.70.4.1.1.5.0')
		if queryResult is not None:
			if len(queryResult) >= 16:
				infoTime = map(lambda x : (not bool(int(x, 16) / 10)) * '0' + str(int(x, 16)), struct.unpack('2x 4s 2s 2s 2s 2s 2s ' + str(len(queryResult) - 16) + 'x', queryResult)) 
				formatAdjust = lambda x : x[0] + '-' + x[1] + '-' + x[2] + ' ' + x[3] + ':' + x[4] + ':' + x[5]
				return {'bsLastStartUpTime' : formatAdjust(infoTime)}
			else:
				print 'Wrong data from snmp mib.'
				return None
		else:
			return None

	def snmpCBType(self):
		rst1 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.3')
		rst2 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.2')
		try:
			for oid in list(rst1):
				if rst1[oid] == 'cb':
					oidTail = oid.split('.')[-1]
					break
			return {'Type' : rst2['1.3.6.1.4.1.637.70.4.1.4.4.1.2' + '.' + oidTail]}
		except:
			return {}

	def snmpBBType(self):
		rst1 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.3')
		rst2 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.2')
		listInfo = {}
		if rst1 is not None:
			for oid in list(rst1):
				if rst1[oid] == 'bb':
					oidTail = oid.split('.')[-1]
					listInfo.update({'BB' + oidTail[2] : {'Type' :rst2['1.3.6.1.4.1.637.70.4.1.4.4.1.2' + '.' + oidTail]}})
			return listInfo
		else:
			return {}

	def snmpRRHVersion(self):
		rst1 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.3')
		rst2 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.2')
		listInfo = {}
		if rst1 is not None:
			for oid in list(rst1):
				if rst1[oid] == 'rrh':
					oidTail = oid.split('.')[-1]
					listInfo.update({'RRH-' + oidTail[2] : {'Version' : rst2['1.3.6.1.4.1.637.70.4.1.4.4.1.2' + '.' + oidTail]}})
			return listInfo
		else:
			return {}

	def snmpSFPAmount(self):
		rst1 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.3')
		rst2 = self.snmpClient('getNext', '1.3.6.1.4.1.637.70.4.1.4.4.1.2')
		hwSFPList = []
		if rst1 is not None:
			for oid in list(rst1):
				if rst1[oid] == 'sfp':
					hwSFPList.append(oid.split('.')[-1])
			return {'SFP_Amount' : len(hwSFPList)}
		else:
			return {}

	def snmpOamCurrIpAddress(self):
		queryResult = self.snmpClient('get','1.3.6.1.4.1.637.70.4.1.5.5.1.0')
		if queryResult is not None:
			infoOamIP = reduce(lambda x, y: x + '.' + str(int(y, 16)), struct.unpack('2s 2s 2s 2s 2s', queryResult))[3:]
			return {'OAM_IP' : infoOamIP}
		else:
			return None

if __name__ == '__main__':
	ins = getInfo('10.9.38.200')
	ins.sshClient.chgSuMode()
	# ins.ssh2BBInfo()
