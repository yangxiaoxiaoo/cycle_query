#!/usr/bin/env python

import sys
import os
import numpy as np
import math

## We need matplotlib:
## $ apt-get install python-matplotlib
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt

## -- Read input
import argparse
parser = argparse.ArgumentParser(description='Plotting script')

parser.add_argument('-ib', nargs='+', dest="impl_list_bounded", default=[], help="list of implementations with bounded data structure size")
parser.add_argument('-iu', nargs='+', dest="impl_list_unbounded", default=[], help="list of implementations with unbounded data structure size")
parser.add_argument('-b', action="store_true", dest='batch_flag', default=False, help="Vertical line for batch ranking")
parser.add_argument('-o', action="store", dest="outFileName", default="out", help="Name of output files")
parser.add_argument('-t', action="store", dest="title", default="", help="Title of figure")
parser.add_argument('-x', action="store", dest="xLabel", default="", help="Label of x axis")
parser.add_argument('-y', action="store", dest="yLabel", default="", help="Label of y axis")

arg_results = parser.parse_args()
impl_list_bounded = arg_results.impl_list_bounded
impl_list_unbounded = arg_results.impl_list_unbounded
batch_flag = arg_results.batch_flag
outFileName = arg_results.outFileName
title = arg_results.title
xLabel = arg_results.xLabel
yLabel = arg_results.yLabel


## First find batch
if batch_flag:
	f = open("outs/batch_ranking.out", "r")
	line = f.readline()
	tokens = line.split()
	batch = float(tokens[2])

k_list_bounded = {}
k_list_unbounded = {}
data = {}

for impl in impl_list_bounded:
	data[impl] = []
	k_list_bounded[impl] = []
	f = open("outs/" + impl + ".out", 'r')
	line = f.readline()
	while line:
		if line.startswith("k ="):
			tokens = line.split()
			data[impl].append(float(tokens[4]))
			k_list_bounded[impl].append(float(tokens[2]))
		line = f.readline()
	f.close()

for impl in impl_list_unbounded:
	data[impl] = []
	k_list_unbounded[impl] = []
	f = open("outs/" + impl + ".out", 'r')
	line = f.readline()
	while line:
		if line.startswith("k ="):
			tokens = line.split()
			data[impl].append(float(tokens[4]))
			k_list_unbounded[impl].append(float(tokens[2]))
		line = f.readline()
	f.close()


fig, ax = plt.subplots()


for i in range(len(impl_list_bounded)):
	plt.plot(data[impl_list_bounded[i]], k_list_bounded[impl_list_bounded[i]], linestyle="--", label=impl_list_bounded[i])

for i in range(len(impl_list_unbounded)):
	ax.plot(data[impl_list_unbounded[i]], k_list_unbounded[impl_list_unbounded[i]], linestyle="--", label=impl_list_unbounded[i])

if batch_flag:
	plt.axvline(x=batch, label='batch ranking', linestyle = "-", color="black")

if title != "":
	plt.title(title)
if yLabel != "":
	plt.ylabel(yLabel)
if xLabel != "":
	plt.xlabel(xLabel)

if (title == "Any-k sort ranked list implementations, Path Query, n=50, l=5"): plt.xlim(0,6)
plt.legend()
plt.savefig(outFileName + ".pdf", format="pdf", bbox_inches="tight")
plt.savefig(outFileName + ".png", format="png", bbox_inches="tight")
