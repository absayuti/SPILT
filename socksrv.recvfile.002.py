#!/usr/bin/python
#
# SPILT server (sockect programming, client-server type)
#
# Version 0.02 11 August 2016
#				Returning 'ok' as acknowledment after receiving filename from client
#				Probabbly will fix the garbled fname + source code problem
#
from __future__ import print_function
import socket               # Import socket module
import time

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                 # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
s.listen(30)                # Now wait for client connection.
print('Listening on port '+ str(port))
while True:
    c, addr = s.accept()     # Establish connection with client.
    print( datetime.datetime.now() )
    print('Got connection from: ')
    print( addr )
    fname = c.recv(1024)
    print("Received fname: " + fname)
    s.send('Ready')
    f = open( fname,'wb')
    print("Receiving file contents ", end='')
    l = c.recv(1024)
    while( l ):
        print(" .", end='')
        f.write(l)
        l = c.recv(1024)
    f.close()
    print("\nDone Receiving")
    c.send('Thank you')
    c.close()                # Close the connection
