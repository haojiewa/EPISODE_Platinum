#/usr/bin/env python
#coding=utf-8
import sys
import multiprocessing
import threading
import os
import configparser
import record_db as db
import imple_ctrl_db as dbc
import imple_opt_main as opt
import logic_process_maintain as mt
from datetime import datetime
import time

global gCfg

class engineStart:
	def __init__(self, runType):
		self.runType = runType
		self.routine()

	def routine(self):
		doRoutineEvent = mt.doRoutineEvent()
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-117', 'ip': '10.44.0.66', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-196', 'ip': '10.44.1.142', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-401', 'ip': '10.44.5.2', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-337', 'ip': '10.44.3.226', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-204', 'ip': '10.44.1.174', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-190', 'ip': '10.44.1.118', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-389', 'ip': '10.44.4.194', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-357', 'ip': '10.44.4.66', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-111', 'ip': '10.44.0.42', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-402', 'ip': '10.44.5.6', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-224', 'ip': '10.44.2.14', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-228', 'ip': '10.44.2.30', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-227', 'ip': '10.44.2.26', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-400', 'ip': '10.44.4.238', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-197', 'ip': '10.44.1.146', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-304', 'ip': '10.44.3.94', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-340', 'ip': '10.44.3.238', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-334', 'ip': '10.44.3.214', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-333', 'ip': '10.44.3.210', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-191', 'ip': '10.44.1.122', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-335', 'ip': '10.44.3.218', 'site' : 'SH-CL'})
		# doRoutineEvent.addNewPltf({'pltf_name': 'SH-CL-ENB-339', 'ip': '10.44.3.234', 'site' : 'SH-CL'})

		doRoutineEvent('updInstantInfo')
		pass

class initCfg(object):
	def __init__(self):
		self.config = configparser.ConfigParser()
		self.configPath = os.path.dirname(os.path.realpath(__file__)) + '/config.ini'
		self.config.read_file(open(self.configPath))
		self.createDBCfg()
		self.createLabCfg()
		self.createECCM2Cfg()
		self.createBCAM2Cfg()

	def createDBCfg(self):
		self.dbhost = self.config.get('MongoDB', "host")
		self.dbusr = self.config.get('MongoDB', "usr")
		self.dbpwd = self.config.get('MongoDB', "pwd")
		self.dbport = self.config.get('MongoDB', "port")
		self.dbname = self.config.get('MongoDB', "database")
		self.dbpool = self.config.get('MongoDB', "max_pool_size")
		self.dbtimeout = self.config.get('MongoDB', "timeout")

	def createLabCfg(self):
		self.labsite = self.config.get('Lab', "site")

	def createECCM2Cfg(self):
		self.ECCM2username = self.config.get('ECCM2', "username")
		self.ECCM2password = self.config.get('ECCM2', "password")
		self.ECCM2supassword = self.config.get('ECCM2', "supassword")
		self.ECCM2prompt = self.config.get('ECCM2', "prompt")
		self.ECCM2port = self.config.get('ECCM2', "port")
	
	def createBCAM2Cfg(self):
		self.BCAM2username = self.config.get('BCAM2', "username")
		self.BCAM2password = self.config.get('BCAM2', "password")
		self.BCAM2supassword = self.config.get('BCAM2', "supassword")
		self.BCAM2prompt = self.config.get('BCAM2', "prompt")
		self.BCAM2port = self.config.get('BCAM2', "port")

	def createDBbsc(self):
		return dbc.optBscInfo(db.actionBscInfo())
		
class dbInstance:
	def __init__(self, site):
		self.configPath = self.getConfig()
		self.configDB = site
		print self.configDB, self.configPath

	def getConfig(self):
		configPath = os.path.dirname(os.path.realpath(__file__)) + '/config.ini'
		return configPath

	def createDBbsc(self):
		return dbc.optBscInfo(db.actionBscInfo(self.configPath, self.configDB))

gCfg = initCfg()

if __name__ == '__main__' :
	print 'Start'
	try:
		main = engineStart(sys.argv[1])
	except:
		main = engineStart(None)