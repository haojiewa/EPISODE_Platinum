#/usr/bin/env python
#coding=utf-8
import os
import configparser
import logic_main_start as main
from pymongo import MongoClient
import cal_basic as bf
import time

class mongodb:
	def __init__(self):
		self.gCfg = main.gCfg

	def __connect(self):
		mongoURL = 'mongodb://' + self.gCfg.dbusr + ':' + self.gCfg.dbpwd + '@' + self.gCfg.dbhost + ':' + self.gCfg.dbport + '/' + self.gCfg.dbname
		clientDatabase = MongoClient(mongoURL, connectTimeoutMS = 60 * 60 * int(self.gCfg.dbtimeout))[self.gCfg.dbname]
		return clientDatabase

	def find(self, table, searchPara1, searchPara2 = {}, limit = None):
		dbTarget = self.__connect()[table]
		result = dbTarget.find(searchPara1, searchPara2)
		resultLen = result.count();
		return result, resultLen

	def findOne(self, table, searchPara1, searchPara2 = {}):
		dbTarget = self.__connect()[table]
		return dbTarget.find_one(searchPara1, searchPara2)

	def insert(self, table, setValue):
		dbTarget = self.__connect()[table]
		return dbTarget.insert(setValue)

	def remove(self, table, searchPara):
		dbTarget = self.__connect()[table]
		return dbTarget.remove(searchPara)

	def update(self, table, searchPara, setValue):
		dbTarget = self.__connect()[table]
		return dbTarget.update(searchPara, {"$set": setValue})

class actionBscInfo(mongodb):
	def __init__(self):
		mongodb.__init__(self)

	def chkDuplItemByCfg(self, pltf_name, ip, site):
		if bf.chkValidIP(ip):
			listPltf_name = {'Cfg.Register_Name' : pltf_name}
			listIP = {'Cfg.Debug_IP' : ip}
			listSite = {'Cfg.Site' : site}
			setContent = {'$and' : [{"$or" : [listPltf_name, listIP]}, listSite]}
			result, resultLen = self.find('pltf_basic_info', setContent)
			if resultLen == 0:
				return True
			else:
				return False
		else:
			return False

	def chkItemByContent(self, content):
		result, resultLen = self.find('pltf_basic_info', content)
		if(resultLen != 0):
			print 'Exist!'
			return True
		else:
			print 'Not Exist!'
			return False

	def delItemByCfg(self, pltf_name, ip, site):
		setContent = {"$and" : [{'Cfg.Debug_IP' : {"$in" : [ip] , "$exists" : 'true'}}, {'Cfg.Register_Name' : {"$in" : [pltf_name] , "$exists" : 'true'}}, {'Cfg.Site' : {"$in" : [site] , "$exists" : 'true'}}]}
		result = self.remove('pltf_basic_info', setContent)
		print result

	def delItemByID(self, _id):
		setContent = {'_id' : _id}
		result = self.remove('pltf_basic_info', setContent)
		print result

	def insNewItem(self, content):
		setContent = {'Refresh_Time' : bf.timeStamp(), 'Cfg' : {'Register_Name' : content['pltf_name'], 'Debug_IP' : content['ip'], 'Site' : content['site']}}
		_id = self.insert('pltf_basic_info', setContent)
		return {'record_id' : _id}

	def qryItemIDByCfg(self, pltf_name, ip):
		setContent1 = {"$and" : [{'Cfg.Debug_IP' : {"$in" : [ip] , "$exists" : 'true'}}, {'Cfg.Register_Name' : {"$in" : [pltf_name] , "$exists" : 'true'}}, {'Cfg.Site' : {"$in" : [site] , "$exists" : 'true'}}]}
		setContent2 = {'_id' : 1}	 
		result = self.findOne('pltf_basic_info', setContent1, setContent2)
		if result.get['_id'] is not None:
			return result['_id']
		else:
			return None

	def qryItemByVaildCfg(self, setContent, site):
		searchPara = {"$and" : [{'Cfg.Debug_IP' : {"$exists" : 'true'}}, {'Cfg.Register_Name' : {"$exists" : 'true'}}, {'Cfg.Site' : {"$in" : [site] , "$exists" : 'true'}}]}
		result, resultLen = self.find('pltf_basic_info', searchPara, setContent)
		return result, resultLen

	def updCfgByID(self, record_id, pltf_name = None, ip = None):
		searchPara = {'_id' : record_id}
		setContent = {'Refresh_Time' : bf.timeStamp()}
		if pltf_name is not None:
			setContent.update({'Cfg.Register_Name' : pltf_name})
		if ip is not None:
			setContent.update({'Cfg.Debug_IP' : ip})
		self.update('pltf_basic_info', searchPara, content)
		return True

	def updItemByID(self, content, record_id):
		searchPara = {'_id' : record_id}
		content.update({'Refresh_Time' : bf.timeStamp()})
		self.update('pltf_basic_info', searchPara, content)
		return True

	def updItemByCfg(self, content, pltf_name, ip):
		searchPara = {"$and" : [{'Cfg.Debug_IP' : {"$in" : [ip] , "$exists" : 'true'}}, {'Cfg.Register_Name' : {"$in" : [pltf_name] , "$exists" : 'true'}}]}
		content.update({'Refresh_Time' : bf.timeStamp()})
		self.update('pltf_basic_info', searchPara, content)
		return True

if __name__ == '__main__' :
	pass