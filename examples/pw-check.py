"""
pw-check will test the given password on the VeraCrypt container or header
either using the values given for PIM, encryption mode, and hashing algorithm
or their defaults if not specified.
s given against a file to determine if it would
successfully decode a TrueCrypt/VeraCrypt volume. This also allows you to 
see if the standard and backup headers match. 

GitHub: https://github.com/wdouglascampbell/pyveracrypt

Usage:
  pw-check <file> [--pim PIM] [--crypto CRYPTO] [--algo ALGO] <password>
 
Options:
  -h, --help                     Show this screen.
  -a ALGO, --algo ALGO           Hashing algorithm
  -c CRYPTO, --crypto CRYPTO     Encryption mode
  -p PIM, --pim PIM              Personal Iterations Multiplier (PIM) value

PIM default value is 458

Hashing algorithms (algo)
 + ripemd
 + sha256
 + whirlpool
 
Encryption modes (crypto)
 + aes (default)
 + serpent
 + twofish
 + aes-twofish
 + aes-twofish-serpent
 + serpent-aes
 + serpent-twofish-aes
 + twofish-serpent
"""

from pyveracrypt import *
from docopt import docopt
import binascii
import six
import appdirs
import packaging
import packaging.version
import packaging.requirements
import packaging.specifiers

if __name__ == '__main__':
    arguments = docopt(__doc__)
    file = arguments['<file>']
    if arguments['--pim']:
        pim = int(arguments['--pim'])
    else :
        pim = 485
    if arguments['--crypto']:
        crypto = arguments['--crypto'].split('-')
    else:
        crypto = ["aes"]
    if arguments['--algo']:
        algo = arguments['--algo']
    else:
        algo = 'sha512'
    password = arguments['<password>']
    
    tc = PyVeracrypt(file, pim, crypto, algo)
    if tc.open(password, False, False):
        print 'correct'
    else :
        print 'incorrect'