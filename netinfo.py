#! /usr/bin/python

###############################################################################
#                                                                             #
#  Copyright (C) 2008-2010  Daniel Kaefer                                     #
#                                                                             #
#  This program is free software: you can redistribute it and/or modify       #
#  it under the terms of the GNU General Public License as published by       #
#  the Free Software Foundation, either version 3 of the License, or          #
#  (at your option) any later version.                                        #
#                                                                             #
#  This program is distributed in the hope that it will be useful,            #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#  GNU General Public License for more details.                               #
#                                                                             #
#  You should have received a copy of the GNU General Public License          #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

import sys
import os
import subprocess
import threading
import urllib2

###############################################################################
#                                                                             #
#                              Some System Calls                              #
#                                (Only Linux)                                 #
#                                                                             #
###############################################################################


def getLocalIPs():
	shell = "ip addr |grep \"inet \"|awk '{ print $2 }'"
	p = subprocess.Popen([shell], shell=True, bufsize=1024, stdout=subprocess.PIPE, close_fds=True)
	p.wait()
	ips = []
	oldIPs = p.stdout.read().splitlines()
	for ip in oldIPs:
		ips.append(ip[0:ip.find("/")])

	return ips

def getRouters():
	shell = "ip route |grep default |awk '{print $3}'"
	p = subprocess.Popen([shell], shell=True, bufsize=1024, stdout=subprocess.PIPE, close_fds=True)
	p.wait()
	return p.stdout.read().splitlines()

def getDNSs():
	shell = "cat /etc/resolv.conf |grep nameserver |awk '{ print $2 }'"
	p = subprocess.Popen([shell], shell=True, bufsize=1024, stdout=subprocess.PIPE, close_fds=True)
	p.wait()
	return p.stdout.read().splitlines()

def getTestIPs():
	return ["193.99.144.80"]

def getTestURLs():
	return ["www.heise.de"]

def ping(ipAddress):
	return os.system("ping -c1 $1>/dev/null 2>&1 " + ipAddress)

###############################################################################
#                                                                             #
#                             Some Helper Class                               #
#                                                                             #
###############################################################################

class Task(threading.Thread):

	def __init__(self, ipAddress, name):
		threading.Thread.__init__(self)
		self.ipAddress = ipAddress
		self.name = name
		self.status = None
		self.start()

	def __str__(self):
		self.join()
		result = self.name + " (" + self.ipAddress + "):"
		result = result.ljust(68)
		if 0 == self.status:
			result += "[ \033[1;322m  up  \033[0m ]"
		else:
			result += "[ \033[1;31m down \033[0m ]"
		return result

class PingTask(Task):

	def run(self):
		self.status = ping(self.ipAddress)

class HttpTask(Task):

	def __init__(self, ipAddress):
		Task.__init__(self, ipAddress, "Http")

	def run(self):
		url = "http://" + self.ipAddress
		try:
			request = urllib2.Request(url)
			handle = urllib2.urlopen(request)
			handle.read()
			handle.close()
			self.status = 0
		except urllib2.URLError:
			self.status = 1


###############################################################################
#                                                                             #
#                               Top Level Function                            #
#                                                                             #
###############################################################################

def usage():
	print("Usage: online.py { show | version | test | usage }")

def version():
	print("Version: 0.5 (2009-03-04)")
	print("Author:  Daniel Kaefer")

def show():
	for localIP in getLocalIPs():
		print("LocalIP: \t", localIP)

	for router in getRouters():
		print("Router: \t", router)

	for dns in getDNSs():
		print("DNS:    \t", dns)

def test():
	tasks = []
	for localIP in getLocalIPs():
		tasks.append(PingTask(localIP, "LocalIP"))

	for router in getRouters():
		tasks.append(PingTask(router, "Router"))

	for dns in getDNSs():
		tasks.append(PingTask(dns, "DNS"))

	for testIP in getTestIPs():
		tasks.append(PingTask(testIP, "TestIP"))

	for testURL in getTestURLs():
		tasks.append(PingTask(testURL, "TestURL"))

	for testURL in getTestURLs():
		tasks.append(HttpTask(testURL))
	

	for task in tasks:
		print(str(task))

###############################################################################
#                                                                             #
#                                     Main                                    #
#                                                                             #
###############################################################################

if 1 == len(sys.argv):
	show()
elif 2 < len(sys.argv):
	usage()
	exit(1)
elif "show" == sys.argv[1]:
	show()
elif "version" == sys.argv[1]:
	version()
elif "test" == sys.argv[1]:
	test()
else:
	usage()
	exit(1)

