#!/usr/bin/env python2.7
from __future__ import print_function

from os import path
from subprocess import call

import numpy as np
from PIL import Image

from dreamer import Dreamer
from scanner import Scanner


def main():
	'''
	sets the structure for going through the dream process step by step
	'''
	fullname = get_name(kind='in') # read in filename
	outname = get_name(kind='out') # read in output name
	opts = get_options() # read in options

	# start dream computations
	s = Scanner() # new scanner
	s.read_alpha_png(fullname) # read and store location of transparent pixels

	my_image = Image.open(fullname, 'r') # open image

	d = Dreamer(my_image) # create new dreamer with reference to image object
	
	img = iterate(d, my_image, outname, opts, save=False) # this function is for iterating over the same image multiple times

	out = s.cut_jpg(img) # send dream buffer object to be cut into transparent PNG

	new_image = Image.new('RGBA', my_image.size) # new blank image of same dimensions
	new_image.putdata(out) # make new image from the information from s.cut_jpg
	new_image.save(outname) # export image

	print("\nsaved image as: %s" % outname)

	open_image(outname) # give user option to automatically open image


# HELPERS --------------------------------------------------------------------------------


def iterate(dream, image, name, options, times=1, save=True):
	'''
	iterate over the same image a specified number of times
	images get stranger and stranger with each pass...
	'''
	for i in xrange(times):
		name = name[:-4] # cut off extension

		if i > 0: # only add number if it's not the first image
			name += "%2d" % i # add number to save name
		
		name += '.jpg'

		new_img = dream.get_dream(octaves=options['octs'], octave_scale=options['os'], end_key=options['ek'])
		dream.set_image(new_img) # set the dream image to the current pass

		if save:
			image.putdata(new_img)
			image.save(name)

			print("\nsaved image as: %s" % name)

	return new_img


def get_options():
	'''
	prompts user to enter custom deepdream settings (or not)
	gets deepdream() options, repeats each until answer is properly formatted
	'''
	out = {'os': None, 'ek': None, 'octs': None} 

	if check_answer("\ndefault number of iterations is 4.\nenter custom number of iterations?"): # user wants to input settings
		while out['octs'] is None:
			read = raw_input("number of octave iterations [1 - 10] > ")
			if read.isdigit():
				read = int(read)
				if read > 0 and read <= 10:
					out['octs'] = read
				else:
					print_error(read, 'not in the given range')
			else:
				print_error(read, 'not an integer')
	else:
		out['octs'] = 4

	if check_answer("\ndefault octave scale is 1.4.\nenter custom octave scale?"): # user wants to input settings
		while out['os'] is None: # loop each until set successfully
			read = raw_input("enter octave_scale (float) [0.1 - 10.0] > ")
			try:
				dig = float(read)
				if dig > 0.0 and dig < 10.0:
					out['os'] = dig
				else: 
					print_error(read, 'not in the given range')
			except: 
				print_error(read, 'not a float')
	else:
		out['os'] = 1.4

	if check_answer("\ndefault effect is 'streak'.\nenter custom streak effect?"): # user wants to input settings
		while out['ek'] is None:
			print("end layer key options (listed in order of increasing computational expenditure): ")
			print(Dreamer.layers.keys())

			read = raw_input("enter end layer key > ")

			if read in Dreamer.layers.keys():
				out['ek'] = read
			else: 
				print_error(read, 'not a valid key')
	else:
		out['ek'] = 'streaks'

	print("\noptions: %s\n" % out)
	return out

def get_name(kind='in'):
	'''
	gets filenames for both input and outputs, based on input parameter
	repeats the question until it gets a real answer, then returns the filename
	'''
	filename = ''

	if kind == 'in':
		while filename == '':
			print("enter an input filename (with extension).")
			print("[ file should be in inputs/ folder, do not include inputs/ in path ]")
			filename = raw_input("> ") # get filename from user
			filename = "inputs/%s" % filename
			if not path.isfile(filename):
				print_error(filename, 'not a real file')
				filename = ''

		print("located input image: %s" % filename)
	elif kind == 'out':
		filename = raw_input("\nenter a name to save new image when complete (no extension) > ")
		filename = "outputs/%s.png" % filename # hardcoded path to outputs/ folder

	return filename


def open_image(img_name):
	''' attempted to get a timeout working, maybe revisit later... maybe
	ATTEMPT ONE

	def exit_open_image(): 
		print('interrupt')
		interrupt_main()

	clock = Timer(5, exit_open_image) 
	clock.start()

	ATTEMPT TWO

	ans = select.select([sys.stdin], [], [], 10)
	print(sys.stdin)
	sys.stdin.flush()
	'''
	get = raw_input("open newly saved image? (y or n) > ")
	if get in ('y', 'Y', 'yes'): # user wants to open image
		call(['open', img_name])


def check_answer(message):
	get = raw_input("%s (y or n) > " % message)
	if get in ('y', 'Y', 'yes'): # user wants to input settings
		return True
	else: return False # by default


def print_error(user_input, problem):
	print("%s is %s. please try again.\n" % (user_input, problem))


# END -------------------------------------------------------------------------------------


if __name__ == '__main__':
	print('\n- - - - - begin deepdream - - - - -\n')
	main()
	print('\n- - - - - goodnight deepdream - - - - -\n')

