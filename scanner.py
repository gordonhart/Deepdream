#!/usr/bin/env python2.7
from __future__ import print_function

from PIL import Image
import numpy as np

class Scanner:
	'''
	scans the input PNG for alpha pixels and stores their locations
	takes a JPG format of the same picture, cuts out the stored alpha pixels,
	and re-outputs to a PNG
	'''

	def __init__(self):
		self.alpha_pix = []
		self.is_alpha = True # assume image has transparency until proven otherwise


	def read_alpha_png(self, png_name):
		'''
		takes a PNG input and stores the location of transparent pixels
		'''
		im = Image.open(png_name, 'r') # open image
		pix_val = list(im.getdata()) # read image pixels to list of tuples (R, G, B, A)


		if len(pix_val[0]) < 4: # if there's no fourth channel, this is RGB
			self.alpha_pix = [255 for i in xrange(0,len(pix_val))] # list of length with full alpha 
			self.is_alpha = False # there is no transparency so we can skip cut_jpg
		else: # RGBA picture (PNG with alpha)
			for pix in pix_val:
				self.alpha_pix.append(pix[3]) # save transparency of each pixel

		return self.alpha_pix


	def cut_jpg(self, jpg_object):
		'''
		takes a jpeg buffer object and cuts out the stored alpha pixels,
		returning a PNG buffer object
		'''
		jpg_img = Image.fromarray(np.uint8(jpg_object))
		jpg_pix = list(jpg_img.getdata()) # read pixels
		
		if self.is_alpha: # there is transparency, go through the remapping
			out_pix = [] # empty output array

			print("\ntrimming transparency...")
			for i in xrange(len(jpg_pix)):
				new_pixel = (jpg_pix[i][0], jpg_pix[i][1], jpg_pix[i][2], self.alpha_pix[i]) # new pixel with color and saved alpha
				out_pix.append(new_pixel)

		else:
			out_pix = jpg_pix

		return out_pix

