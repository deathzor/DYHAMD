import filesystem
import blockdevice
print "WARING: this system provides no encryption what so ever in its current stage so it provides Zero in terms of security and posible overwrites it one file data there for this should not be used on any production system";
print "WARING THIS CODE IS PRE-ALPHA AND SHOULD BE CONSIDERED TO BE WITHOUT ANY WARRENTY SO I'm NOT RESPONSIBLE FOR ANY DAMAGE DIRECT OR INDIRECT DONE TO ANYTHING BY THE USAGE OF THIS CODE"; 

blockdev = blockdevice.blockdevice('/tmp/ruberfuse');
ruberfuse = filesystem.main(blockdev);
#this line is to create a new index table
#ruberfuse.create_table_index('mykey2');
ruberfuse.load_table_index('mykey2');
if (ruberfuse.create_file_index('myname2','this is my file') != 0):
	print 'error creating file';
print ruberfuse._findfile();

