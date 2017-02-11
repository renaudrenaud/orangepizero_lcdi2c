# orangepizero_lcdi2c
Managing an i2C LCD 16x2 with an Orange Pi Zero
----
Before we start, we need to install python specific package. This package includes header files, a static library and development tools. In particular Pyhton.h is required to install the GPIO software.

FOR ORANGE PI ZERO WITH DEBIAN

1/ add in /etc/modules 
i2c-bcm2708
i2c-dev

2/ reboot

3/ add gpio module:
sudo modprobe gpio-sunxi 

4/ add python smbus:
sudo apt-get install python-smbus

4/ install tool for reading address:
sudo apt-get install i2c-tools

5/ read address of I2C LCD
sudo i2cdetect -y 0

6/ install python installer package
sudo apt-get install python-pip 

7/ add setutools of xenial (not required for Debian)
sudo apt-get install python-setuptools

8/ add pylms
sudo pip install pylms

9/there is an error (2 in fact) in pylms package:
in the /usr/local/lib/python2.7/dist-packages/pylms/server.py file, around line 100, replace with thses 2 lines:
 import unicodedata
 result = unicodedata.normalize('NFKD', result).encode('ascii','ignore')

10/ get the wrapper for the GPIO for OPZ :
https://github.com/nvl1109/orangepi_PC_gpio_pyH3/tree/1bb13a6bfaa13c05efc5bd1dd685ecda14b95358/pyA20

11/ install it:
sudo python setup.py install

12 finished!!!
------------------------------------ USAGE

lms_testcom.py
  -s <ipserver>
  -p <ipplayer>
  -w <lcd_width>
  -w <lcd_width>
    ipserver like 192.168.1.102
    player like 192.168.1.115 / no parameter = player n°1
    lcd with is 16 or 20 / 16 means 16x2, 20 means 20x4
    lcd_address is the i2C LCD address like 0x3f. Use sudo i2cdetect -y 0

example : sudo python -s 192.168.1.120 -p 192.168.1.104 -w 20
