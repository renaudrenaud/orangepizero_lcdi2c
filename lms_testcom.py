
from pylms.server import Server
from pylms.player import Player
from time import sleep
# import readchar ???
import smbus
import time
import sys, getopt
import signal

class LCD:
    """LCD Class build from the work of Math Hawkins"""
    def __init__(self, lcd_address):
		# Define some device parameters
       
        self.I2C_ADDR  = lcd_address # 0x3f I2C device address 
                                     # To detect use sudo i2cdetect -y 0
                                     # or for RPi 2  sudo i2cdetect -y 1
        self.LCD_WIDTH = 16   # Maximum characters per line

        # Define some device constants
        self.LCD_CHR = 1 # Mode - Sending data
        self.LCD_CMD = 0 # Mode - Sending command

        self.LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
        self.LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
        self.LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
        self.LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

        self.LCD_BACKLIGHT  = 0x08  # On
        #LCD_BACKLIGHT = 0x00  # Off

        self.ENABLE = 0b00000100 # Enable bit

        # Timing constants
        self.E_PULSE = 0.0005
        self.E_DELAY = 0.0005

        #Open I2C interface
        self.bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
        #bus = smbus.SMBus(1) # Rev 2 Pi uses 1

        #def lcd_init():
        # Initialise display
        self.lcd_byte(0x33,self.LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32,self.LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06,self.LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C,self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
        self.lcd_byte(0x28,self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01,self.LCD_CMD) # 000001 Clear display
        time.sleep(self.E_DELAY)

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        # bits = the data
        # mode = 1 for data
        #        0 for command
        

        self.bits_high = mode | (bits & 0xF0) | self.LCD_BACKLIGHT
        self.bits_low = mode | ((bits<<4) & 0xF0) | self.LCD_BACKLIGHT

        # High bits
        try:
            self.bus.write_byte(self.I2C_ADDR, self.bits_high)
        except:
            print ("------------------------------------------")
            print ("ERROR - Cannot write on the LCD @ Address " + self.I2C_ADDR )
            print ("------------------------------------------")
            printhelp()
            quit()
        self.bus.write_byte(self.I2C_ADDR, self.bits_high)
        self.lcd_toggle_enable(self.bits_high)

        # Low bits
        self.bus.write_byte(self.I2C_ADDR, self.bits_low)
        self.lcd_toggle_enable(self.bits_low)

    def lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(self.E_DELAY)
        self.bus.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.I2C_ADDR,(bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def lcd_string(self, message, line):
        # Send string to display
        message = message.ljust(self.LCD_WIDTH," ")
        if line == 1:
            self.lcd_byte(self.LCD_LINE_1, self.LCD_CMD)
        elif line == 2:
            self.lcd_byte(self.LCD_LINE_2, self.LCD_CMD)
        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]),self.LCD_CHR)



def lms_time_to_string(lms_time ):
    "covert a time from LMS into a mm:ss time"
    seconds = int(lms_time)
    minutes = int(seconds / 60)
    seconds = seconds - minutes * 60
    if seconds < 10 :
            seconds = "0" + str(seconds)
    if minutes < 10 :
        minutes = "0" + str(minutes)
    return "%s:%s" %(minutes, seconds)

import sys, getopt
def printhelp():
    """Print help to explain parameters"""
    print ("------------ USAGE ---------------------------------------------")
    print ("lms_testcom.py ")
    print ("-s <ipserver>")
    print ("-p <ipplayer>")
    print ("-l <lcd_address>")
    print ("-w <lcd_width>")
    print ("ipserver like 192.168.1.102")
    print ("player like 192.168.1.115 / no parameter = player n*1") 
    print ("lcd_address is the i2C LCD address like 0x3f. Use sudo i2cdetect -y 0") 
    print ("lcd with is 16 or 20 / 16 means 16x2, 20 means 20x4")
    print ("----------------------------------------------------------------")

def main(argv):
    """MAIN LCD MANAGER APP FOR LMS"""
    # signal.signal(signal.SIGTERM, sigterm_handler) # to manage the app as a service
    lmsserver = ""
    lmsplayer = ""
    lcd_address = "0x3f"
    lcd_w = 16
    try:
        opts, args = getopt.getopt(argv,"hs:p:l:",["server=","player=","lcd_address"])
    except getopt.GetoptError:
        printhelp()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            printhelp()
            sys.exit()
        elif opt in ("-s", "--server"):
            lmsserver = arg
        elif opt in ("-p", "--player"):
            lmsplayer = arg
        elif opt in("l","--lcd_address"):
            lcd_address = arg
        elif opt in("w","--lcd_width"):
            lcd_w = arg    
    myLCD = LCD(int(lcd_address,16))
    #myLCD.lcd_string"1234567890123456",1)
    myLCD.lcd_string("   TVC Audio    ",1)
    myLCD.lcd_string("  LMS LCD INFO  ",2)
    sleep(2)
    myLCD.lcd_string("(C)2017 Renaud  ",1)
    myLCD.lcd_string("Coustellier     ",2)
    sleep(1)
    myLCD.lcd_string("Initializing",1)
    myLCD.lcd_string("Please wait",2)
    if lmsserver =="":
        lmsserver = "192.168.1.134"

    sc = Server(hostname=lmsserver, port=9090, username="user", password="password")

    test_con = 1
    test_max = 5
    while test_con < test_max :
        try:
            sc.connect()
            myLCD.lcd_string("LMS SERVER",1)
            myLCD.lcd_string(lmsserver,2)
            sleep(1)
            test_con = test_max
        except:
            test_con = test_con + 1
            print ("cannot connect to the server @" + lmsserver )
            #myLCD.lcd_string"1234567890123456",1)
            myLCD.lcd_string("not connected " ,1)
            myLCD.lcd_string("try " + str(test_con) + " / 5" ,2)
            sleep(3)
            myLCD.lcd_string(lmsserver,2)
            
            sleep(3)
            if test_con == test_max:
                printhelp()
                quit(0)

    print ("Logged in: %s" % sc.logged_in )
    print ("LMS Version: %s" % sc.get_version())

    #myLCD.lcd_string"1234567890123456",1)

    myLCD.lcd_string("LMS v.: %s" % sc.get_version(),2)
    sleep(2)

    if sc.get_player_count() > 0:
        print ("Players; %d" % sc.get_player_count())
        print (sc.get_players(True))
        myLCD.lcd_string("Players count %d" % sc.get_player_count(),2)
        sleep(2)
    else:
        print ("No Player connected")
        fline = False
        while sc.get_player_count() == 0:
            if fline == True:
                fline = False
            else:
                fline = True
            if fline == True:
                myLCD.lcd_string("No player cncted",1)
            else:
                myLCD.lcd_string("svr" + lmsserver,1)
            myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M:%S'),2)
            sleep(2)
        
    
    players = []
    players = sc.get_players(True)   
    p = 0
    if lmsplayer == "":
         sq = players[0]
    else:
        
        players = sc.get_players(True)   
       
        for player in players:
            ipplayer = str(players[p].get_ip_address())
            ipplayer = ipplayer[0:ipplayer.find(":")]
            myLCD.lcd_string("found player",1)
            myLCD.lcd_string(ipplayer,2)
            print (ipplayer)
            sleep(2)    
            if ipplayer == lmsplayer:
                sq = players[p]
            p = p + 1

    myLCD.lcd_string("connected to p" + str(p + 1) ,1)
    myLCD.lcd_string(sq.get_name(),2)
    sleep(2)

    print ("Name: %s | Mode: %s | Time: %s | Connected: %s | WiFi: %s"
        % (sq.get_name(), sq.get_mode(), sq.get_time_elapsed(),
            sq.is_connected, sq.get_wifi_signal_strength()))

    
    print ("player ip:" + sq.get_ip_address())
    #print sq.get_rate()
    print ("mac " + sq.get_ref())

    print (sq.get_mode())

    while True:
        try:

            modePlayer = sq.get_mode()  
            if modePlayer == "pause":
                
                #print ('\r'"mode = pause - " + time.strftime('%Y-%m-%d %H:%M:%S'),end='')
                #myLCD.lcd_string("1234567890123456",1)
                myLCD.lcd_string("mode = pause",1)
                myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M:%S'),2)
                sleep(2)
            elif modePlayer == "stop":
                #print ('\r'"mode = stop " + time.strftime('%Y-%m-%d %H:%M:%S'),end='')
                myLCD.lcd_string("mode = stop",1)
                myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M:%S'),2)
                sleep(2)
            elif modePlayer == "play":
                trackAlbum = sq.get_track_album()
                currentTrack = sq.get_track_current_title()
                trackArtist = sq.get_track_artist()
                currentVolume = sq.get_volume()

                print ("")
                print ("album:" + trackAlbum)
                print ("artist:" + trackArtist)
                print ("title:" + currentTrack)

                #myLCD.lcd_string("1234567890123456",1)
                myLCD.lcd_string("Alb." + trackAlbum,1)
                myLCD.lcd_string("Art." + trackArtist,2)
                sleep(2)
                myLCD.lcd_string(trackAlbum,1)
                myLCD.lcd_string(trackArtist,2)
                
                td =  "/" + lms_time_to_string(sq.get_track_duration())        
                
                linestatus = 0
                charOffset = 0
                while True:
                    linestatus = linestatus + 1
                    volume = (" - Volume %" + str(sq.get_volume()) )
                    te =  "time " + lms_time_to_string(sq.get_time_elapsed())
                    #print ('\r'"time " + te + td + volume, end ='')
                    while currentVolume != sq.get_volume():
                        # Volume
                        myLCD.lcd_string("Volume %" + str(sq.get_volume()), 1)    
                        currentVolume = sq.get_volume()
                        sleep(1)
                    if linestatus < 2:
                        myLCD.lcd_string("tle:" + currentTrack, 1)
                        myLCD.lcd_string(te + td, 2)
                    elif linestatus < 15:
                        # Track Name
                        if len(currentTrack) <= lcd_w:
                            # LENGHT is < LCD LCD_WIDTH
                            myLCD.lcd_string(currentTrack, 1)
                        else:
                            # LENGHT is > LCD_WIDTH
                            charOffset = linestatus - 2
                            myLCD.lcd_string(currentTrack[charOffset:], 1)    
                        myLCD.lcd_string(te + td, 2)    
                    elif linestatus < 20:
                        if len(trackAlbum) <= lcd_w:
                            myLCD.lcd_string(trackAlbum,1)
                        else:
                            charOffset = linestatus - 15
                            myLCD.lcd_string(trackAlbum[charOffset:], 1) 

                        myLCD.lcd_string(trackArtist,2)     
                    elif linestatus >= 23:
                        linestatus = 0
                    if sq.get_track_current_title() != currentTrack or sq.get_mode() !="play" :
                        # change detected
                        myLCD.lcd_string("Track/mode chang", 1)
                        myLCD.lcd_string("pls wait...     ", 2)
                        break
                    sleep(1)
        except:
            print("error -->", sys.exc_info()[0])
            myLCD.lcd_string("Sorry error", 1)
            myLCD.lcd_string(sys.exc_info()[0], 2)
            quit(0)

if __name__ == "__main__":
    
    main(sys.argv[1:])        
