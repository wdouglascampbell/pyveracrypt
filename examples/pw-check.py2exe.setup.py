from distutils.core import setup # Need this to handle modules
import py2exe 
# We have to import all modules used in our program
from pyveracrypt import *
from docopt import docopt
import binascii
import wmi
from lib.vcdefs import *
from lib.win32defs import *
import ctypes
import re
import six
import appdirs
import packaging
import packaging.version
import packaging.requirements
import packaging.specifiers

setup(
    console=['pw-check.py'],
    zipfile = None,
    options={
        "py2exe":{
            "bundle_files":1,
            'compressed': True,
            'dll_excludes':['w9xpopen.exe']
        }
    }
) # Calls setup function to indicate that we're dealing with a single console application