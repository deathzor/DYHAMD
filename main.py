import filesystem
ruberfuse = filesystem.main();
ruberfuse.setblockdevice('/tmp/ruberfuse');
#this line is to create a new index table
#ruberfuse.create_table_index('mykey2');
ruberfuse.load_table_index('mykey2');
if (ruberfuse.create_file_index('myname2','this is my file') != 0):
	print 'error creating file';
	print ruberfuse._findfile();

