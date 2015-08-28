# /usr/bin/env python
# coding=utf-8

from pysnmp.entity.rfc3413.oneliner import cmdgen
import re

class eNB_SNMP:
	AUTH_PROTOCOL_REGISTRY = {
		'MD5': cmdgen.usmHMACMD5AuthProtocol,
		'SHA': cmdgen.usmHMACSHAAuthProtocol,
		None: cmdgen.usmNoAuthProtocol,
		'': cmdgen.usmNoAuthProtocol,
		False:cmdgen.usmNoAuthProtocol,
	}

	PRIV_PROTOCOL_REGISTRY = {
		'DES': cmdgen.usmDESPrivProtocol,
		None: cmdgen.usmNoPrivProtocol,
		'': cmdgen.usmNoPrivProtocol,
		False:cmdgen.usmNoPrivProtocol,
	}

	def __init__(self, ip, port="161", user="initial_snm", authpass="@t9n;_EBQb", privpass=None, authProtocol="SHA", privProtocol=None, timeout=1, retries=5):
		self.SNMP_Auth(user, authpass, privpass, authProtocol, privProtocol)
		self.SNMP_Target(ip, port, timeout, retries)

	def __call__(self, method, Oid):
		if method in ['get', 'getNext', 'getBulk']:
			if re.compile("^(\d|\.)+$").match(Oid):
				return getattr(self, method)(Oid)
			else:
				print 'Error Input: Wrong Oid!'
		else:
			print 'Error Input: Wrong method!'

	def SNMP_Auth(self, user=None, authpass=None, privpass=None, authProtocol=None, privProtocol=None):
		if authpass == None:
			authProtocol = None
		if privpass == None:
			privProtocol = None
		authProtocol = self.AUTH_PROTOCOL_REGISTRY[ authProtocol ]
		privProtocol = self.PRIV_PROTOCOL_REGISTRY[ privProtocol ]
		self.Auth = cmdgen.UsmUserData(user, authProtocol=authProtocol, authKey=authpass, privProtocol=privProtocol, privKey=privpass)

	def SNMP_Target(self, ip, port="161", timeout=1, retries=5):
		self.Target = cmdgen.UdpTransportTarget((ip, port), timeout, retries)

	def get(self, Oid, Auth=None, Target=None):
		if Auth == None:
			Auth = self.Auth
		if Target == None:
			Target = self.Target
		errorIndication, errorStatus, errorIndex, varBindTableRow = cmdgen.CommandGenerator().getCmd(Auth,Target,Oid)
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				try:
					print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBindTableRow[-1][int(errorIndex)-1][0] or '?'))
				finally:
					return None
			else:
				return list(varBindTableRow)[0][1].prettyPrint()

	def getNext(self, Oid, Auth=None, Target=None):
		if Auth == None:
			Auth = self.Auth
		if Target == None:
			Target = self.Target
		return_dic = {}
		errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().nextCmd(Auth,Target,Oid)
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				try:
					print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBindTable[-1][int(errorIndex)-1][0] or '?'))
				finally:
					return None
			else:
				for varBindTableRow in varBindTable:
					for name, val in varBindTableRow:
						return_dic[name.prettyPrint()] = val.prettyPrint()
				return return_dic

	def getBulk(self, Oid, Auth=None, Target=None, nonRepeaters=0, maxRepetitions=15):
		if Auth == None:
			Auth = self.Auth
		if Target == None:
			Target = self.Target
		return_dic = {}
		errorIndication, errorStatus, errorIndex, varBindTable = cmdgen.CommandGenerator().bulkCmd(Auth,Target, nonRepeaters, maxRepetitions, Oid)
		if errorIndication:
			print(errorIndication)
		else:
			if errorStatus:
				try:
					print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBindTable[-1][int(errorIndex)-1][0] or '?'))
				finally:
					return None
			else:
				for varBindTableRow in varBindTable:
					for name, val in varBindTableRow:
						return_dic[name.prettyPrint()] = val.prettyPrint()
				return return_dic