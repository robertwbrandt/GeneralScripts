#!/usr/bin/python

import sys, smtplib

msg = ''
while 1:
	line = sys.stdin.readline()
	if not line:
		break

	if line[:6] == "From: ": fromaddr = line[6:]
	if line[:4] == "To: ": toaddr = line[4:]
	if line[:8] == "Server: ": 
		smtpserver = line[8:]
	else:
		msg = msg + line

# The actual mail send
server = smtplib.SMTP(smtpserver, 25)
server.sendmail(fromaddr, [ toaddrs ], msg)
server.quit()

#print fromaddr
#print toaddr
#print smtpserver
#print msg
