from __future__ import print_function

# imports and basic notebook setup
from cStringIO import StringIO
import numpy as np
import scipy.ndimage as nd
import PIL.Image
from IPython.display import clear_output, Image, display
from google.protobuf import text_format

import caffe

import sys
from collections import OrderedDict


class Dreamer:
	'''
	reads image and returns dream
	'''
	layers = OrderedDict() #define names of interesting layers
	layers['streaks']	= "conv2/3x3_reduce" # impressionist
	layers['kaleido']	= "inception_3a/pool" # colorful triangular scales
	layers['geo_swirl']	= "inception_3b/pool_proj" # blocky, yet swirly...
	layers['blocky']	= "inception_3b/3x3_reduce"
	layers['banding']	= "inception_3b/5x5_reduce"
	layers['swirls']	= "inception_4a/1x1"
	layers['eyes']		= "inception_4c/1x1"
	layers['standard']	= "inception_4c/output" # probably the best for getting images 
	layers['shapes']	= "inception_4e/pool" # technically more deep than standard, but not as good


	def __init__(self, img_object):
		'''
		sets up deep learning environment
		(init with reference to existing PIL image object)
		'''
		self.model_path = '../../caffe/caffe/models/bvlc_googlenet/' # path to caffe model
		self.net_fn   = self.model_path + 'deploy.prototxt'
		self.param_fn = self.model_path + 'bvlc_googlenet.caffemodel'

		self.model = caffe.io.caffe_pb2.NetParameter() # Patching model to be able to compute gradients
		text_format.Merge(open(self.net_fn).read(), self.model)
		self.model.force_backward = True

#		print "write tmp.prototxt"
		open('tmp.prototxt', 'w').write(str(self.model))

		self.net = caffe.Classifier('tmp.prototxt', self.param_fn, 				
			mean = np.float32([120.0, 120.0, 120.0]), # change mean values to balance out colors
			channel_swap = (2,1,0)) # mess with color channels

		img_object = img_object.convert('RGB') # convert to RGB image object just in case it was passed as RGBA
		self.img = np.float32(img_object)
		showarray(self.img)


	def get_dream(self, octaves=4, octave_scale=1.6, end_key='streaks'):
		'''
		return a dream image buffer object
		'''
		end_layer = Dreamer.layers[end_key]
		frame = self.img
		frame = deepdream(self.net, frame, octave_n=octaves, octave_scale=octave_scale, end=end_layer)
		
		return frame

	def get_image(self): return self.img
	def set_image(self, _img): self.img = _img


# END CLASS ----------------------------------------------------------------------------------------

# GLOBAL FUNCTIONS ---------------------------------------------------------------------------------


def deepdream(net, base_img, iter_n=8, octave_n=4, octave_scale=1.4, end='inception_4c/output', clip=True, **step_params):
	'''
	this is where the magic happens.
	iterates through each octave, and each iteration within each octave
	returns an image buffer object
	'''
	print("\n< < < begin deepdream\n")

	# silly array to give names to loop numbers
	names = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']

	octaves = [preprocess(net, base_img)] # prepare base images for all octaves
	print("number of octaves: %d" % octave_n)

	for i in xrange(octave_n-1):
		octaves.append(nd.zoom(octaves[-1], (1, 1.0/octave_scale,1.0/octave_scale), order=1))

	src = net.blobs['data']
	detail = np.zeros_like(octaves[-1]) # allocate image for network-produced details

	print("\nenter octave enumeration loop")
	print("number of iterations for each octave: %d\n" % iter_n)

	for octave, octave_base in enumerate(octaves[::-1]):
		h, w = octave_base.shape[-2:]
		if octave > 0:
			# upscale details from the previous octave
			h1, w1 = detail.shape[-2:]
			detail = nd.zoom(detail, (1, 1.0*h/h1,1.0*w/w1), order=1)

		src.reshape(1,3,h,w) # resize the network's input image size
		src.data[0] = octave_base+detail

		for i in xrange(iter_n):
			print("\rcomputing %s octave (%d/%d)..." % (names[octave], i+1, iter_n), end='')
			sys.stdout.flush() # sends line to STDOUT despite python's output buffering (also python -u would work)
			
			make_step(net, end=end, clip=clip, **step_params) # try much, much higher 'jitter' value
#			make_step(net, step_size=(0.25*i), end=end, clip=clip, **step_params) # try much, much higher 'jitter' value

			vis = deprocess(net, src.data[0]) # visualization
			if not clip: # adjust image contrast if clipping is disabled
				vis = vis*(255.0/np.percentile(vis, 99.98))
			showarray(vis)
		    
		print("\roctave %d complete [end layer=%s, size=%s]" % (octave+1, end, vis.shape))
		detail = src.data[0]-octave_base # extract details produced on the current octave

	print("\n> > > end deepdream")
	return deprocess(net, src.data[0]) # returning the resulting image


def make_step(net, step_size=1.5, end='inception_4c/output', jitter=32, clip=True):
	'''
	Basic gradient ascent step.
	'''
	src = net.blobs['data'] # input image is stored in Net's 'data' blob
	dst = net.blobs[end]

	ox, oy = np.random.randint(-jitter, jitter+1, 2)
	src.data[0] = np.roll(np.roll(src.data[0], ox, -1), oy, -2) # apply jitter shift

	net.forward(end=end)
	dst.diff[:] = dst.data # specify the optimization objective
	net.backward(start=end)
	g = src.diff[0]

	src.data[:] += step_size/np.abs(g).mean() * g # apply normalized ascent step to the input image

	src.data[0] = np.roll(np.roll(src.data[0], -ox, -1), -oy, -2) # unshift image

	if clip:
		bias = net.transformer.mean['data']
		src.data[:] = np.clip(src.data, -bias, 255-bias) 


def showarray(a, fmt='jpeg'):
	a = np.uint8(np.clip(a, 0, 255))
	f = StringIO()
	PIL.Image.fromarray(a).save(f, fmt)


# utility functions for converting to and from Caffe's input image layout
def preprocess(net, img): return np.float32(np.rollaxis(img, 2)[::-1]) - net.transformer.mean['data']
def deprocess(net, img): return np.dstack((img + net.transformer.mean['data'])[::-1])


# END -------------------------------------------------------------------------------------

