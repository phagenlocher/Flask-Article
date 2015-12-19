#!/usr/bin/python3

from time import time
from statistics import mean
from flask_article import ScriptLoader

def print_result(result):
	print('| Min (in seconds)\t| Mean (in seconds)\t| Max (in seconds)\t|')
	print('| --------------------- | --------------------- | --------------------- |')
	print('|',min(result),'\t|',mean(result),'\t|',max(result),'\t|')

def test_script_loader(sl, iterations):
	print('Timing get_article_list...')
	result = []
	for i in range(iterations):
		t1 = time()
		a = sl.get_article_list()
		t2 = time()
		result.append(t2-t1)
	print_result(result)

	print('Timing get_single_script...')
	result = []
	for i in range(iterations):
		t1 = time()
		sl.get_single_script('test1')
		t2 = time()
		result.append(t2-t1)
	print_result(result)

##
iterations = 100
##

print("Testing with caching...")
sl = ScriptLoader(script_folder='test', caching=True, debug=False)
test_script_loader(sl, iterations)

print("\n\nTesting without caching...")
sl = ScriptLoader(script_folder='test', caching=False, debug=False)
test_script_loader(sl, iterations)