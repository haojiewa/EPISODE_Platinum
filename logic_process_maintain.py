#/usr/bin/env python
#coding=utf-8
import logic_main_start as main
import imple_opt_main as opt
from multiprocessing import Process

class doRoutineEvent(object):
	def __init__(self):
		gCfg = main.gCfg
		self.dbbsc = gCfg.createDBbsc()
		self.site = gCfg.labsite
		self.callList = ['addNewPltf', 'updInstantInfo']

	def __call__(self, operation, *args, **kwargs):
		if operation in self.callList:
			doThis = getattr(self, operation)
			return doThis(kwargs)
		else:
			print 'class doRoutineEvent method is not in the call list!'

	def addNewPltf(self, content):
		if content.get('site') == None:
			content['site'] = self.site
		result = self.dbbsc.new(content)
		if result is None:
			print '_id is empty!'
			return False
		else:
			return True

	def updInstantInfo(self, params):
		listIP = self.dbbsc('listAsLite', self.site)
		print listIP
		mplist = []
		for record in listIP:
			mpIns = Process(target = reflashBscInfo, args = (record[0], record[1], record[2]))
			mplist.append(mpIns)
			mpIns.start()
		for ins in mplist:
			ins.join(120)
			if ins.is_alive():
				ins.terminate()
		print 'Multiprocess done.'

class reflashBscInfo(object):
	def __init__(self, record_id, ip, name, runLevel = 'High'):
		gCfg = main.gCfg
		self.dbbsc = gCfg.createDBbsc()
		self.ip = ip
		self.tIns = opt.getInfo(ip)
		self.do(record_id, ip, name, runLevel)

	def do(self, record_id, ip, name, runLevel):
		infoList = {}
		runFunGroupList = ['reflashStatusInfo', 'reflashCBInfo', 'reflashBBInfo', 'reflashRRHInfo', 'reflashConfInfo', 'reflashOtherInfo']
		if runLevel == 'High':
			operationList = runFunGroupList
		elif runLevel == 'Test':
			operationList = ['reflashBBInfo']
		if self.tIns.sshStatus is not 'off':
			for fun in operationList:
				doThis = getattr(self, fun)
				result =  doThis()
				if result is not None:
					infoList.update(result)
				print ip, fun
			if self.dbbsc('update', infoList, record_id):
				print ip, name
			else:
				print ip, infoList
		else:
			pass

	def reflashBBInfo(self):
		infoBBSubList = {}
		result = self.tIns('ssh2BBInfo')
		infoBB2SubList, infoBB3SubList, infoBB4SubList = self._sortBB(result)
		result = self.tIns('sshBBInfo')
		infoBB2SubList, infoBB3SubList, infoBB4SubList = self._sortBB(result, infoBB2SubList, infoBB3SubList, infoBB4SubList)
		result = self.tIns('snmpBBType')
		infoBB2SubList, infoBB3SubList, infoBB4SubList = self._sortBB(result, infoBB2SubList, infoBB3SubList, infoBB4SubList)
		if infoBB2SubList != {}:
			infoBBSubList.update({'BB2' : infoBB2SubList})
		if infoBB3SubList != {}:
			infoBBSubList.update({'BB3' : infoBB3SubList})
		if infoBB4SubList != {}:
			infoBBSubList.update({'BB4' : infoBB4SubList})
		if infoBBSubList != {}:
			return {'BB' :infoBBSubList}
		else:
			return {'BB' : None}

	def _sortBB(self, result, infoBB2SubList = {}, infoBB3SubList = {}, infoBB4SubList = {}):
		if result is not None:
			if isinstance(result, dict):
				for infoKey in result.keys():
					if infoKey[0:2] == 'BB':
						if infoKey[2] == '2':
							if result.get(infoKey) is not None:
								for subInfoKey in result.get(infoKey).keys():
									infoBB2SubList.update({subInfoKey:result.get(infoKey).get(subInfoKey)})
						elif infoKey[2] == '3':
							if result.get(infoKey) is not None:
								for subInfoKey in result.get(infoKey).keys():
									infoBB3SubList.update({subInfoKey:result.get(infoKey).get(subInfoKey)})
						elif infoKey[2] == '4':
							if result.get(infoKey) is not None:
								for subInfoKey in result.get(infoKey).keys():
									infoBB4SubList.update({subInfoKey:result.get(infoKey).get(subInfoKey)})
						else:
							pass
					else:
						pass
			else:
				pass
		return infoBB2SubList, infoBB3SubList, infoBB4SubList

	def reflashCBInfo(self):
		infoCBList = {}
		result = self.tIns('snmpCBType')
		if result == None:
			result = self.tIns('sshCBType')
		else:
			pass
		if result != None:
			infoCBList.update(result)
		funList = ['sshUptimeInfo', 'sshCBSN', 'sshCBTN', 'sshCBVN', 'sshCBCpuUsage', 'sshCBMemUsage', 'sshCcmPCBver', 'sshCcmMirRel']
		for fun in funList:
			result = self.tIns(fun)
			if result != None:
				infoCBList.update(result)
		if infoCBList != {}:
			return {'CB' : infoCBList}
		else:
			return None


	def reflashConfInfo(self):
		infoConfList = {}
		result = self.tIns('snmpOamCurrIpAddress')
		if result == None:
			result = self.tIns('sshOamIp')
		else:
			pass
		if result != None:
			infoConfList.update(result)
		result = self.tIns('sshS1Ip')
		if result != None:
			infoConfList.update(result)
		for fun in ['sshD2UVerInfo', 'sshDBUInfo', 'snmpEnbFriendlyName']:
			result = self.tIns(fun)
			if result != None:
				infoConfList.update(result)
		if infoConfList != {}:
			return {'Conf' : infoConfList}
		else:
			return None

	def reflashOtherInfo(self):
		infoOtherList = {}
		result = self.tIns('sshRsi')
		if result != None:
			infoOtherList.update(result)
		result = self.tIns('sshFreq')
		if result != None:
			infoOtherList.update(result)
		result = self.tIns('sshCfg')
		if result != None:
			infoOtherList.update(result)
		result = self.tIns('snmpSFPAmount')
		if result != None:
			infoOtherList.update(result)
		if infoOtherList != {}:
			return {'Other' : infoOtherList}
		else:
			return None

	def reflashRRHInfo(self):
		infoRRHList = {}
		RRHNameList = []
		result = self.tIns('sshRRHInfo')
		if result is not None:
			for infoKey in result.keys():
				if infoKey[0:3] == 'RRH':
					infoRRHList.update({infoKey:result.get(infoKey)})
					RRHNameList.append(infoKey)
		if infoRRHList != {}:
			infoRRHList.update({'RRH_List' : RRHNameList})
			return {'RRH' : infoRRHList}
		else:
			return None

	def reflashStatusInfo(self):
		infoStatusList = {}
		result = self.tIns('snmpLoadVersionInfo')
		if result == None:
			result = self.tIns('sshLoadVersionInfo')
		else:
			pass
		if result != None:
			infoStatusList.update(result)
		result = self.tIns('snmpBsLastStartUpTime')
		if result != None:
			infoStatusList.update(result)
		result = self.tIns('snmpResetReason')
		if result != None:
			infoStatusList.update(result)
		result = self.tIns('sshGpsStatusInfo')
		if result != None:
			infoStatusList.update(result)
		if infoStatusList != {}:
			return {'Status' : infoStatusList}
		else:
			return None			