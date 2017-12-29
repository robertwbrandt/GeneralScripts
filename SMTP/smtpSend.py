#!/usr/bin/env python
"""
	Python script to send emails.
"""
import smtplib
import argparse
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


parser = argparse.ArgumentParser(description='Send HTML email to a remote SMTP server.')
parser.add_argument('-f','--from', help='From Address', required=True)
parser.add_argument('-t','--to', help='To Address', required=True)
parser.add_argument('-s','--subject', help='Subject', default="Python HTML Email")
parser.add_argument('-S','--server', help='SMTP Server', default="smtp")
parser.add_argument('-H','--html', help='HTML File', required=True)
args = vars(parser.parse_args())

FROM    = args['from']
TO      = args['to']
SUBJECT = args['subject']
SMTP    = args['server']
HTML    = args['html']

# Create the body of the message (a plain-text and an HTML version).
TEXT = "This is a HTML email"
with open (args['html'], "r") as myfile:
    HTML=myfile.read()

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = SUBJECT
msg['From'] = FROM
msg['To'] = TO
msg['X-Priority'] = '1'


# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(TEXT, 'plain')
part2 = MIMEText(HTML, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Send the message via SMTP server.
s = smtplib.SMTP(SMTP)
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
s.sendmail(FROM, TO, msg.as_string())
s.quit()
