#!/usr/bin/python
###############################################################################
#
# SPILT server (sockect programming, client-server type)
# (AB Sayuti HM Saman)
#	
# This script need to be run on the server during LABTEST. To make things 
# easier to manage, copy this file into a folder at home directory, like so:
#
#       $ mkdir ~/dec2025
#       $ cd ~/dec2025
#       $ cp srv/pub/spilt/tools/socksrv.recvfile.005.py .
#
# Thus, this script can be run like so (assuming you are already in the said 
# folder):
#
#       $ python3 socksrv.recvfile.005.py
#			      
###############################################################################
#			
# Version 0.05 22 Dec 2025
# 		Porting the whole !@#$#@ to a new set of server+clients
#		We are running on new PCs, new Ubuntu and new Python3!	             
#		
###############################################################################
from __future__ import print_function
import socket               # Import socket module
import datetime, time

s = socket.socket()         # Create a socket object
#host = socket.gethostname() # Get local machine name
host = '172.17.9.41'        # Key in in this server's IP address manually
port = 12345                # Reserve a port for our service.
s.bind((host, port))        # Bind to the port
s.listen(30)                # Now wait for client connection.
print('Listening on port '+ str(port))
while True:
	c, addr = s.accept()     # Establish connection with client.
	print()
	print( datetime.datetime.now() )
	print('\tGot connection from: ', end='')
	print( addr )
	fname = c.recv(40)
	fname = fname.rstrip()	# Remove trailing spaces
	print('\tReceived fname: "' + fname.decode() +'"')	
	f = open( fname,'wb')
	print("\tReceiving file contents ", end='')
	l = c.recv(1024)
	while( l ):
		print(" .", end='')
		f.write(l)
		l = c.recv(1024)
	f.close()
	print("\n\tDone Receiving")
	time.sleep(1)            # was c.send('Thank you.')
	c.close()                # Close the connection
