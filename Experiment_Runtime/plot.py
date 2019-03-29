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

parser.add_argument('-i', nargs='+', dest="impl_list", default=[], help="list of implementations")
parser.add_argument('-b', action="store", dest='batchFile', default=None, help="Vertical line for batch ranking")
parser.add_argument('-l', nargs='+', dest="label_list", default=[], help="list of implementation names (put batch last if specified!)")
parser.add_argument('-o', action="store", dest="outFileName", default="out", help="Name of output files")
parser.add_argument('-t', action="store", dest="title", default="", help="Title of figure")
parser.add_argument('-x', action="store", dest="xLabel", default="", help="Label of x axis")
parser.add_argument('-y', action="store", dest="yLabel", default="", help="Label of y axis")

arg_results = parser.parse_args()
impl_list = arg_results.impl_list
batchFile = arg_results.batchFile
label_list = arg_results.label_list
outFileName = arg_results.outFileName
title = arg_results.title
xLabel = arg_results.xLabel
yLabel = arg_results.yLabel


## First find batch
if batchFile != None:
	f = open("outs/" + batchFile, "r")
	line = f.readline()
	tokens = line.split()
	batch = float(tokens[2])

k_list = {}
data = {}

for impl in impl_list:
	data[impl] = []
	k_list[impl] = []
	f = open("outs/" + impl, 'r')
	line = f.readline()
	while line:
		if line.startswith("k ="):
			tokens = line.split()
			data[impl].append(float(tokens[4]))
			k_list[impl].append(float(tokens[2]))
		line = f.readline()
	f.close()


fig, ax = plt.subplots()

for i in range(len(impl_list)):
	ax.plot(data[impl_list[i]], k_list[impl_list[i]], linestyle="--", label=label_list[i])

if batchFile != None:
	plt.axvline(x=batch, linestyle = "-", color="black", label=label_list[-1])

if title != "":
	plt.title(title)
if yLabel != "":
	plt.ylabel(yLabel)
if xLabel != "":
	plt.xlabel(xLabel)
plt.legend()
plt.savefig(outFileName + ".pdf", format="pdf", bbox_inches="tight")
plt.savefig(outFileName + ".png", format="png", bbox_inches="tight")
