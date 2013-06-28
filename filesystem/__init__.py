#!/usr/bin/python

import StringIO
from time import time

import random
import stat    # for file properties
import os      # for filesystem modes (O_RDONLY, etc)
import errno   # for error number codes (ENOENT, etc)
from Crypto.Hash import SHA512
from Crypto import Random
import struct

#FIXME i only work on a blockdevice 
class main:
	def __init__(self,device):
		#FIXME static size
		self.disksize = (10737418240 / 1024) / 1024;
		#i should be given to init
		self.blockdevice = device;
		self.freeblocks = {0:self.disksize};
	def load_table_index(self,key):
		#FIXME no overlap check currently 
		hash = SHA512.new(key);
		self.blockdevice.seek(0);
		self.blockdevice.seek(self._hash_to_location(hash.hexdigest()));
		hextowrite = ord(self.blockdevice.read(1));
		self.indexlocation = hextowrite * (512 * 1024) + 2;
	def _hash_to_location(self,hash2):
		#FIXME no overlap check currently
		hash2 = int(hash2,16);
		output = StringIO.StringIO();
		output.write(hash2)
		output.seek(0)
		return int(output.read(8),10);	
	def create_table_index(self,key):
		#FIXME no overlap check currently 
		hash = SHA512.new(key);
		self.blockdevice.seek(0);
		self.blockdevice.seek(self._hash_to_location(hash.hexdigest()));
		hextowrite = random.randint(2,255);
		self.blockdevice.write('%c' % hextowrite);
		self.indexlocation = hextowrite * (512 * 1024) + 2;
	def _free_table_slot(self):
		#FIXME prevent the off change that you find this key in decrypted randomdata.
		output = str(ord(self.blockdevice.read(1)))+str(ord(self.blockdevice.read(1)));
		#print hex(self.blockdevice.tell());
		self.blockdevice.seek(-2,1);
		#print hex(self.blockdevice.tell());
		#this is 0F0F
		#print output
		if (output == '1515'):
			#move the cursor to a empty slot recursive function might create a stackoverflow on large disks
			#FIXME max number of jumps before we need a jump point. 
			self.blockdevice.seek(100,1);
			self._free_table_slot();
		#this is 1F1F and there for a directory
		if (output == '3131'):
			self.blockdevice.seek(100,1);
			self._free_table_slot();
	def reserved_blockcheck(self,block):
		#FIX ME i'm not really checking the block
		challange = 0
		highchallange = self.disksize;
		succes = 0
		#loop over the dictonary to get some important values
		#print self.freeblocks;
		for (key,item) in self.freeblocks.iteritems():
			if (key > block or key == block):
				if (key < highchallange):
					highchallange = key;
			if (key < block):
				if (key > challange):
					challange = key;
				if (item > block):
					succes = 1;
		if (highchallange != block):
			#split the blocks if the byte next to it is unclaimed 
			tempblock = self.freeblocks[challange];
			self.freeblocks[challange] = block - 1;
			self.freeblocks[block + 1] = tempblock;
		else:
			#merge the arrays
			self.freeblocks[challange] = self.freeblocks[highchallanger];
			#check if there is more then 1 block i here
			if (self.freeblocks[highchallange] > highchallange):
				#make a new array moved 1 item 
				self.freeblocks[highchallange + 1] =  self.freeblocks[highchallange]
			#remove the old array
			del(self.freeblocks[highchallange]);
				
			
		if (succes == 1):
			return block
		else:
			return self.reserved_blockcheck(random.randint(128,self.disksize));
	def _followpath(self,path):
		#strip the zero paths
		if (len(path) == 0):
			return self.indexlocation;
		else:
			for x in self._findfile(self.indexlocation):
				if (path[0][0] == x[0]):
					return x[1];	
	def create_directory_index(self,directoryname,path = []):
		#follow the path to the right index
		targetpath = self._followpath(path);
		#CREATE A DIRECTORY INDEX
		for name in self._findfile(targetpath):
			if (name[0] == directoryname):
				return -1;
		self.blockdevice.seek(targetpath,0)
		self._free_table_slot();
		location = int(str(self.blockdevice.tell()),10);
		self.blockdevice.write('%c' % int(str(31),10));
		self.blockdevice.write('%c' % int(str(31),10));
		self.write_empty_name(self.blockdevice.tell());
		self.blockdevice.write(directoryname);
		self.blockdevice.seek(location);
		self.blockdevice.seek(93,1);
		randomblock = self.reserved_blockcheck(random.randint(128,self.disksize));
		size = len(str(struct.pack("I", randomblock)))
		self.blockdevice.write(struct.pack("I", randomblock));
		return 0;
	def write_empty_name(self,location):
		#writes the empty name
		self.blockdevice.seek(location);
		x = 0;
		#loop to write the 08's
		while (x != 92):
			self.blockdevice.write('%c' % 128);
			x = x + 1;
		#set the pointer back
		self.blockdevice.seek(location);
	def write_contents(self,byte,contents):
		#FIXME I ERROR ON FILES LARGE THEN 512 Bytes
		if (len(contents) < 512):
			self.blockdevice.seek(byte,0);
			self.blockdevice.write(struct.pack('I',1515));
			self.blockdevice.write(contents);
			return 0;
		else:
			return -1

	def _findfile(self,location = 0):
		#Reading the file index for know files.
		if (location == 0):
			location = self.indexlocation;
		self.blockdevice.seek(location);
		output = str(ord(self.blockdevice.read(1)))+str(ord(self.blockdevice.read(1)));
		if (output == str(1515) or output == str(3131)):
			self.blockdevice.seek(location + 2);
			temp = "";
			x = 0;
			while(ord(str(x)) != 128):
				x = self.blockdevice.read(1);
				if (ord(str(x)) != 128):
					temp = temp + x;
			#print temp;
			self.blockdevice.seek(location + 100);
			output = str(ord(self.blockdevice.read(1)))+str(ord(self.blockdevice.read(1)));
			if (output == str(1515) or output == str(3131)):
				templist =  self._findfile(location + 100);
			else:
				templist = []
			self.blockdevice.seek(location + 94);
			location = struct.unpack('I',self.blockdevice.read(4))[0] * 1024 * 1024;
			templist.extend([[temp,location]]);
			temp = templist;
			return temp;
		return [];
	def create_file_index(self,filename,contents,path = []):
		#CREATE A FILE INDEX
		targetpath = self._followpath(path);
		for name in self._findfile(targetpath):
			if (name[0] == filename):
				return -1;
		self.blockdevice.seek(targetpath,0)
		self._free_table_slot();
		location = int(str(self.blockdevice.tell()),10);
		self.blockdevice.write('%c' % int(str(15),10));
		self.blockdevice.write('%c' % int(str(15),10));
		self.write_empty_name(self.blockdevice.tell());
		self.blockdevice.write(filename);
		self.blockdevice.seek(location);
		self.blockdevice.seek(93,1);
		randomblock = self.reserved_blockcheck(random.randint(128,self.disksize));
		size = len(str(struct.pack("I", randomblock)))
		self.blockdevice.write(struct.pack("I", randomblock));
		self.write_contents(randomblock * 1024 * 1024,contents);
		return 0;


