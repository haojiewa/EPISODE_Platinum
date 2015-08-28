#/usr/bin/env python
#coding=utf-8

class optBscInfo:
	def __init__(self, dbInstance):
		self.db = dbInstance
		self.callList = ['new', 'delete', 'query', 'update', 'listAsLite']

	def __call__(self, operation, *args, **kwargs):
		if operation in self.callList:
			doThis = getattr(self, operation)
			return doThis(*args, **kwargs)
		else:
			print 'class optBscInfo method is not in the call list!'

	def new(self, content):
		if self.db.chkDuplItemByCfg(content['pltf_name'], content['ip'], content['site']):
			result = self.db.insNewItem(content)
			if(result.get('record_id') is not None):
				return result
			else:
				print 'get record_id Failure!'
				return None
		else:
			print 'Failure! Because dupl!'
			return None

	def delete(self, content):
		if(self.db.chkItemByContent({'Cfg.Debug_IP' : content.get('ip'), 'Cfg.Register_Name' : content.get('pltf_name'), 'Cfg.Site' : content.get('site')})):
			self.db.delItemByCfg(content.get('pltf_name'), content.get('ip'), content.get('site')) 
			return True
		else:
			return False

	def update(self, content, record_id = None):
		if content != {}:
			if record_id is None:
				record_id = self.db.qryItemIDByCfg(content.get('pltf_name'), content.get('ip'), content.get('site'))
			if record_id is not None:
				self.db.updItemByID(content, record_id)
				return True
			else:
				return False
		else:
			return True

	def listAsLite(self, site):
		queryList = []
		setContent = {}
		map(lambda x: setContent.setdefault(x, 1), ['_id', 'Cfg.Debug_IP', 'Cfg.Register_Name'])
		result, resultLen = self.db.qryItemByVaildCfg(setContent, site)
		for record in result:
			oneRow = []
			oneRow.append(record['_id'])
			oneRow.append(record['Cfg']['Debug_IP'])
			oneRow.append(record['Cfg']['Register_Name'])
			queryList.append(oneRow)
		return queryList

	def query(self, showList, searchPara):
		if showList is not None:
			setContent = {}
			queryList = []
			map(lambda x: setContent.setdefault(x, 1), showList.split(','))
			result, resultLen = self.db.find('pltf_basic_info', searchPara, setContent)
			for record in result:
				oneRow = []
				for item in showList.split(','):
					oneRow.append(reduce(lambda x, y :  x.get(y), [record] + item.split('.')))
				if queryList is not None:
					queryList.append(oneRow)
			return queryList

if __name__ == '__main__' :
	import logic_main_start as main
	gCfg = main.gCfg
	dbbsc = gCfg.createDBbsc()
	ip = '10.9.37.234'
	ip = '10.9.37.200'
	# ip = '10.9.37.114'
	searchPara = [{'Cfg.Debug_IP' : ip}, {'Cfg.Site' : gCfg.labsite}]
	result = dbbsc('query', 'CB.CPU_Usage,CB.Type,CB.Mem_Usage,Refresh_Time', {'$and' : searchPara})
	for item in result:
		for subitem in item:
			print subitem
	pass		