# orangepizero_lcdi2c
Managing an i2C LCD 16x2 with an Orange Pi Zero
----
Before we start, we need to install python specific package. This package includes header files, a static library and development tools. In particular Pyhton.h is required to install the GPIO software.

sudo apt-get install python-dev
sudo apt-get install python3-dev
then we install the package for managing gpio and start the GPIO:
sudo python setup.py install 
sudo modprobe gpio-sunxi
sudo apt-get install python-smbus
sudo apt-get install i2c-tools

usage : please use -h for help
-s ipserver -p ipplayer -l address for LCD
