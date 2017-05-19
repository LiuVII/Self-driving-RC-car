#!/bin/usr/env python3
import getch
import os
import time
from urllib.request import urlopen

#Controls for wifi car v1
#pip3 install getch

http = 'http://'
ip = '192.168.2.9'

up = '\033[A'
down = '\033[B'
right = '\033[C'
left = '\033[D'

ot = 0

while True:
	ct = time.time() * 1000
	c = getch.getch()
	if  c == '\033':
		getch.getch()
		c = getch.getch()
		if ct - ot > 500:
			ot = ct
			ret_val = None
			if c == 'A':
				ret_val = urlopen(http+ip+"/fwd/st85")
			elif c == 'B':
				ret_val = urlopen(http+ip+"/rev")
			elif c == 'C':
				ret_val = urlopen(http+ip+"/fwd/rt")
			elif c == 'D':
				ret_val = urlopen(http+ip+"/fwd/lf")
			if (ret_val):
				print(ret_val.read())
	else:
		if c == 's':
			print(urlopen(http+ip+"/st85").read())
