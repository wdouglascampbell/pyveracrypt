"""
pw-check will test the given password on the VeraCrypt encrypted container or
device or on the system either using the values given for PIM, encryption mode, and hashing algorithm
or their defaults, if not specified.

GitHub: https://github.com/wdouglascampbell/pyveracrypt

Usage:
  pw-check file <file> [--pim PIM] [--crypto CRYPTO] [--algo ALGO] <password>
  pw-check system [--pim PIM] [--crypto CRYPTO] [--algo ALGO] <password>
 
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
import wmi
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
    
    if arguments['file']:
        tc = PyVeracrypt(file, pim, crypto, algo)
    if arguments['system']:
        c = wmi.WMI()

        # get system partition drive letter
        wql = "SELECT SystemDrive FROM Win32_OperatingSystem"
        drive_letter = c.query(wql)[0].SystemDrive
        
        # iterate over physical disks, their partitions and those partitions logical drives to find the physical disk that holds the system partition
        for physical_disk in c.Win32_DiskDrive ():
          for partition in physical_disk.associators ("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators ("Win32_LogicalDiskToPartition"):
              if logical_disk.DeviceID == drive_letter:
                disk=physical_disk.DeviceID
                break
        
        tc = PyVeracrypt(disk, pim, crypto, algo, None, True, True)
        
    if tc.open(password, False, False):
        print 'correct'
    else :
        print 'incorrect'
