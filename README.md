# Deepdream

My implementation of Google's [Deepdream](https://github.com/google/deepdream) deep learning image processing software.

## What's New

This Deepdream repository builds upon the standard Google `Deepdream` interface to offer a simple, intuitive and easy-to-use command-line interface for generating custom "dream" images.

After sorting through all of the 80+ `end layers` that are available, I've isolated the 9 most interesting effects and presented them as options for customizing your output. Each `end layer` offers a unique and striking visual effect to generate everything from streaky images in the impressionist style to the classic dogs-everywhere look that made `Deepdream` famous in the first place.

There are other editing options avaiable at the command line as well including the `octaves` (number of passes) and the scale of each `octave`.

Full alpha transparency support for PNGs has also been built in. Supports JPG and PNG images as inputs, and will always output an alpha-enabled PNG image that can be converted to a flat or lossy format (such as JPG) by the user afterwards.

The modular design also allows users to add custom effect modules and have a little fun with low-level image processing. The alpha support module for PNGs can serve as an example of this functionality.

## Usage Instructions

Run with `python main.py` or as an executable `./main.py` and go from there. All input images must be located in the `inputs` folder.

## Dependencies

There are significant dependencies to run `Deepdream`. Most of them involve the installation of the [Caffe](http://caffe.berkeleyvision.org/installation.html) Python module, the Deep Learning framework that was implemented in the creation of this piece of software (Disclaimer: this can be painful. Consider yourself warned). In addition, you must have a working distribution of Python 2.7 installed.

You will also need to install a working Deep Learning training set. See the Berkeley Vision and Learning Center's [Model Zoo](https://github.com/BVLC/caffe/wiki/Model-Zoo) to find a working model.

For more information on dependencies see `requirements.txt`.