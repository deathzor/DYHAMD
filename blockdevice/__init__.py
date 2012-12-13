class blockdevice:
	def __init__(self,path):
		self.target = open(path,'rwb+');
	def write(self,stufftowrite):
		self.target.write(stufftowrite)
	def read(self,byte):
		return self.target.read(byte)
	def seek(self,byte,typ = 0):
		self.target.seek(byte,typ);
