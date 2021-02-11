# Instructions for Building pw-check

## Install Python 2.7.18

Python 2.7.18 is the last release of Python 2.  Download Windows x86 MSI installer from https://www.python.org/downloads/release/python-2718.

During the installation change “Add python.exe to Path” to “Will be installed on local hard drive”.


## Update Pip

Enter the following at a command prompt.

    python -m pip install --upgrade pip


## Install python-setuptools

This may be already installed.

Enter the following at a command prompt.

    pip install setuptools


## Install Microsoft Visual C++ Compiler for Python 2.7

Download from https://aka.ms/vcpython27.


## Install python-cryptoplus Module (required by pyveracrypt)

python-cryptoplus (https://github.com/doegox/python-cryptoplus) can be retrieved using git clone.

Open a command prompt.  Switch to the root folder of the python-cryptoplus module and enter the following:

    pip install .

This will prevent the module from being installed as an .egg file which py2exe does not seem to handle well.


## Install Additional Modules (required by pyveracrypt or pw-check)

    pip install appdirs docopt packaging six wmi


## Install pyveracrypt Module

pyveracrypt (https://github.com/wdouglascampbell/pyveracrypt) can be retrieve using git clone.


## Test

Test by running pw-check.py from the command-prompt.  Keep in mind that to really test this you will need to have VeraCrypt installed and the system encrypted.

1.	Open a command prompt.
2.	Set PYTHONPATH to pyveracrypt directory.

>    set PYTHONPATH=...\path\to\pyveracrypt

3.	Switch to the pyveracrypt\examples directory.
4.	Run pw-check.py.

>    python pw-check.py system --pim 1 \<password\>

Note:	Using the drive and system options require administrator privileges to work since they directly access the system drives.


## Install py2exe

p2exe can be downloaded from its sourceforge page.  Download the last 32-bit release (py2exe-0.6.9.win32-py2.7.exe).


## Build pw-check.exe

1.	Open a command prompt.
2.	Set PYTHONPATH to pyveracrypt directory.

>    set PYTHONPATH="..\path_to_pyveracrypt"

3.	Switch to the pyveracrypt\examples directory.
4.	Build pw-check.exe using the following command:

>    python pw-check.py2exe.setup.py py2exe

Note:	Sometimes it is necessary to run the above command twice due to an access denied error on the first run.

The resulting executable will be found in the pyveracrypt\examples\dist directory.


