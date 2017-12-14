import socket               # Import socket module
import sys

def sendfileviasocket( prgname ):
	
	host = socket.gethostname() # Get local machine name
	port = 12345                 # Reserve a port for your service.

	try: 
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
		s.connect((host,port)) 
	except socket.error, (value,message): 
		if s: 
			s.close() 
		print "Could not open socket: " + message 
		#sys.exit(1)
		return -1

	# s.connect((host, port))
	s.send('copy.of.'+prgname)
	f = open( prgname,'rb')
	print 'Sending...'
	l = f.read(1024)
	while (l):
		print 'Sending...'
		s.send(l)
		l = f.read(1024)
	f.close()
	print "Done Sending"
	s.close
	return 0               

# main starts here -------------------------------------------------------------
rc = sendfileviasocket('program1.c')
print( rc )
