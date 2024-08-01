#!/usr/bin/env python
# coding: utf8

from sys import exit

import numpy as np


def savevar(filename, **kwargs):

	np.save(filename, kwargs)

	return


def loadvar(filename, *args):

	t = [] # list to store values (mask arrays)
	
	#-------------------------------------------------------------------------------
	# To fix error: ValueError: Object arrays cannot be loaded when allow_pickle=False
	# save np.load
	np_load_old = np.load

	# modify the default parameters of np.load
	np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)
	#-------------------------------------------------------------------------------

	d = np.load(filename).item()

	#-------------------------------------------------------------------------------
	# restore np.load for future normal usage
	np.load = np_load_old
	#-------------------------------------------------------------------------------

	for arg in args:
		try:
			t.append(d[arg]) # add values associated to name in arg
		except KeyError:
			exit("KeyError: '%s' is not a variable in '%s'" % (arg, filename))

	return t