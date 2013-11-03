# -*- coding: utf-8 -*-
import os
import time
import smtplib

from email.mime.text import MIMEText

def turn_changed_within(savedir, secs):
	now = time.mktime(time.localtime())
	for files in os.listdir(savedir):
		if files.endswith(".trn"):
			filestat = os.stat(savedir + files)
			lastmodified = now-filestat.st_mtime
			if lastmodified < secs:
				return True
	return False

def send_notifications(props):
	with open(props["receiversfile"], "r") as f:
			receivers = list(map(str.strip, f))
	print "Sending notifications from "+ props["sender"] + " to " + str(receivers)
	smtpconn = smtplib.SMTP(props["host"], props["port"])
	smtpconn.starttls()
	smtpconn.login(props["user"], props["pass"])
	msg = MIMEText(props["message"])
	sender = props["sender"]
	msg['Subject'] = props["subject"]
	msg['From'] = props["sender"]
	smtpconn.sendmail(props["sender"], receivers, msg.as_string())
	smtpconn.quit()

def main():
	props = dict(line.strip().split('=') for line in open('emailnotifier.properties'))
	
	if turn_changed_within(props["savegamedirectory"], float(props["maxsecsold"])):
		print "Turn changed, send email!"
		send_notifications(props)
	else:
		print "No new turn :("

main()
