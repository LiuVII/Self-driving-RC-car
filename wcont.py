#!/bin/usr/env python3
import getch
import os
import time

#Controls for wifi car v1
#pip3 install getch

http = 'http://'
ip = '10.10.10.112'

up = '\033[A'
down = '\033[B'
right = '\033[C'
left = '\033[D'

ot = 0

while True:
	ct = time.time()
	c = getch.getch() 
	if  c == '\033':
		getch.getch()
		c = getch.getch()
		if ct - ot > 1:
			ot = ct
			if c == 'A':
				print("up")
				#os.system('curl '+http+ip+'/fwd')
			elif c == 'B':
				print("down")
				#os.system('curl '+http+ip+'/rev')
			elif c == 'C':
				print("right")
				#os.system('curl '+http+ip+'/fwd/rt')
			elif c == 'D':
				print("left")
				#os.system('curl '+http+ip+'/fwd/lf')