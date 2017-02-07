# orangepizero_lcdi2c
Managing an i2C LCD 16x2 with an Orange Pi Zero
----
Before we start, we need to install python specific package. This package includes header files, a static library and development tools. In particular Pyhton.h is required to install the GPIO software.

sudo apt-get install python-dev
#sudo apt-get install python3-dev
then we install the package for managing gpio and start the GPIO:
sudo python setup.py install 
sudo modprobe gpio-sunxi
sudo apt-get install python-smbus
sudo apt-get install i2c-tools

USAGE 
lms_testcom.py
  -s <ipserver>
  -p <ipplayer>
  -l <lcd_address>
  -w <lcd_width>
    ipserver like 192.168.1.102
    player like 192.168.1.115 / no parameter = player n°1
    lcd_address is the i2C LCD address like 0x3f. Use sudo i2cdetect -y 0
    lcd with is 16 or 20 / 16 means 16x2, 20 means 20x4
