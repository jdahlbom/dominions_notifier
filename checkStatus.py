# -*- coding: utf-8 -*-
import os
import time
import smtplib

from email.mime.text import MIMEText
from subprocess import call					# To execute 7za, the 7-zip commandline compressor
from email.mime.multipart import MIMEMultipart		# For email attachments
from email.mime.base import MIMEBase				#
from email.utils import COMMASPACE, formatdate		#
from email import encoders							#

# snipped from http://stackoverflow.com/questions/3362600/how-to-send-email-attachments-with-python
def send_mail( send_from, send_to, subject, text, files=[], server="localhost", port=587, username='', password='', isTls=True):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime = True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="{0}"'.format(os.path.basename(f)))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if isTls: smtp.starttls()
    if username: smtp.login(username,password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()


def turn_changed_within(savedir, secs):
	now = time.mktime(time.localtime())
	for files in os.listdir(savedir):
		if files.endswith(".trn"):
			filestat = os.stat(savedir +"\\"+ files)
			lastmodified = now-filestat.st_mtime
			if lastmodified < secs:
				return True
	return False

	
def send_notifications(props):
	with open(props["receiversfile"], "r") as f:
			receivers = list(map(str.strip, f))
	print ("Sending notifications from "+ props["sender"] + " to " + str(receivers))
	smtpconn = smtplib.SMTP(props["host"], props["port"])
	smtpconn.starttls()
	smtpconn.login(props["user"], props["pass"])
	msg = MIMEText(props["message"])
	sender = props["sender"]
	msg['Subject'] = props["subject"]
	msg['From'] = props["sender"]
	smtpconn.sendmail(props["sender"], receivers, msg.as_string())
	smtpconn.quit()

	
def send_turnfiles(props):
	receivers = [ line.split() for line in open(props["turnfilereceiversfile"]) ]
	receivers = [ item for item in receivers if len(item) != 0 ]			# Ignore empty lines
	receivers = [ item for item in receivers if (item[0][:1] != '#') ]		# Ignore comment lines
	
	for line in receivers:
		print ("Packing "+line[0] + " --> "+line[1])
		zipfile = props["savegamedirectory"]+"\\"+line[0]+".xz"
		trnfile = props["savegamedirectory"]+"\\"+line[0]+".trn"
		os.remove(zipfile)
		call ("7za a -txz "+zipfile+" "+trnfile, shell=True)
		send_mail( props["sender"], line[1], props["subject"], props["message"], [zipfile], props["host"], isTls=props["smtptls"] )
	
	
def main():
	props = dict(line.strip().split('=') for line in open('emailnotifier.properties'))

	if turn_changed_within(props["savegamedirectory"], float(props["maxsecsold"])):
		print ("Turn changed, send email!")
		send_notifications(props)
		send_turnfiles(props)
		
	else:
		print ("No new turn :(")
		

	
	
main()
