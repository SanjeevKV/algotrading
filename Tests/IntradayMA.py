import os
import sys
import re
import time

class Statistics:
	def __init__(self,val):
		self.prev_val = val
		self.simple_mean = val
		self.simple_ma   = val
		self.last_hour_ma = val
		self.day_ma    = val 


	def simple_statistics(self,val):
		'''Let us say we are getting the stock value every second
		we need to maintain a counter 3600 seconds and then update
		last_hour_average
		'''
		if self.simple_mean == 0:
			self.simple_mean = val
		self.simple_mean = (self.simple_mean + val)/2.0
		self.prev_val = val
		if time.localtime().tm_min == 0 and time.localtime().tm_sec==0 and time.localtime().tm_hour == 9:
			self.simple_mean = self.day_ma
		if time.localtime().tm_min == 0 and time.localtime().tm_sec==0 and time.localtime().tm_hour >= 9 and time.localtime().tm_hour <= 17:
			self.last_hour_ma = self.simple_mean
		if time.localtime().tm_min == 0 and time.localtime().tm_sec==0 and time.localtime().tm_hour == 18:
			self.day_ma = self.last_hour_ma


x = Statistics(0.0)
list = [6, 7, 9, 5, 8, 6, 9]
for i in list:
	x.simple_statistics(i)
print x.simple_mean, x.last_hour_ma, x.day_ma





