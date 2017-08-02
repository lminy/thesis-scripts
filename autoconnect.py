#!/usr/bin/env python

# Requirements :
# sudo pip install netifaces
# sudo apt-get install wireless-tools

SSID = 'ssid'
INTERFACE = 'wlan0'


import subprocess
import re
import time
import logging
 
logger = logging.getLogger("AutoConnect")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("autoconnect.log")
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.info("Starting autoconnect")

#################################
########### FUNCTIONS ###########
#################################

def run(command):
	"""
	Return the output of command
	"""
	p = subprocess.Popen(command.split(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
	return ''.join(iter(p.stdout.readline, b''))

def run_bg(command) :
	"""
	Run the command in background
	"""
	subprocess.Popen(command.split())

def get_ip(interface) :
    import netifaces as ni
    ni.ifaddresses(interface)
    ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
    return ip

def print_line(text) : # https://stackoverflow.com/a/3249684/5955402
	from sys import stdout
	from time import sleep
	stdout.write("\r%s                " % text)
	stdout.flush()

def println(text) :
	from sys import stdout
	from time import sleep
	stdout.write("\n%s\n" % text)
	logger.info(text)


def is_connected(interface) : 
	"""
	# Version 1 : AP Could be out of range and iwconfig can still see it connected...
	output = run("sudo iwconfig %s" % interface)
	if re.search(SSID, output) :
		return True
	else :
		return False
	"""
	# Version 2 : better than 1 but not perfect
	output = run("sudo iwconfig %s" % interface)
	if re.search('Not-Associated', output) :
		return False
	else :
		return True



run("sudo service network-manager stop")
run("sudo ifconfig wlan0 up")


############################
########### MAIN ###########
############################


print 'AUTO-CONNECT on %s' % SSID

was_connected = False
if is_connected(INTERFACE) :
	println("Already connected.  IP=%s" % get_ip(INTERFACE))
	was_connected = True


while True :
	if is_connected(INTERFACE) :
		print_line("Connected")
		was_connected = True
	else :
		if was_connected :
			println("Disconnected")

		print_line("Connecting...")
		error = run("sudo iwconfig wlan0 essid %s" % SSID)
		if(len(error)==0) :
			#print "Connected!"
			run_bg("sudo dhclient wlan0")
			time.sleep(1)
			run("sudo killall dhclient")
			#if "RTNETLINK answers: File exists" in error or error == "" :
			
			#else :
			#	print "Error while getting the IP (dhclient) : " + error
			if is_connected(INTERFACE) :
				println("Connected successfully!     IP : " + get_ip(INTERFACE))
				was_connected = True
			else :
				print_line("Failed to connect")
				was_connected = False
		else :
			print "Error while connecting : " + error
	time.sleep(1)
