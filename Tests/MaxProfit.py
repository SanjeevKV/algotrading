import os
import sys
import re

def max_profit(array):
	mx_profit = 0
	min_so_far = array[0]
	good_sprice = 0
	for ind in range(0,len(array)):
		sprice = array[ind]
		if sprice < min_so_far:
			min_so_far = sprice
			min_so_far_ind = ind
		mx_profit_here = sprice - min_so_far
		if mx_profit_here > mx_profit:
			mx_profit = mx_profit_here
			good_sprice_ind = ind
			good_bprice_ind = min_so_far_ind
	print "Good buy and sell prices indexes",good_bprice_ind, good_sprice_ind
	return mx_profit

if __name__ == '__main__':
	filename = sys.argv[1]
	with open(filename) as file:
		cnt = 0
		for line in file:
			if re.match("Sample",line):
				cnt += 1
				list = []
			elif(re.match(" ",line)):
				pass
			elif re.match("End",line):
				print "Sample ",cnt
				print "Max stock price is ",max(list),
				print "Min stock price is ",min(list)
				print "Max profit that can be booked ",max_profit(list)
			else:
				list = [int(stk_price) for stk_price in line.split(',')]
