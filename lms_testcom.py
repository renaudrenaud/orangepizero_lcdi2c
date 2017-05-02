
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
    def __init__(self, lcd_address, lcd_width):
		# Define some device parameters
       
        self.I2C_ADDR  = lcd_address # 0x3f I2C device address 
                                     # To detect use sudo i2cdetect -y 0
                                     # or for RPi 2  sudo i2cdetect -y 1
        self.LCD_WIDTH = lcd_width   # 16 or 20 Maximum characters per line
        print ("class LCD " + str(lcd_width))    
        #LCD_WIDTH = 20 OR 16   # Maximum characters per line

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
        elif line == 3:
            self.lcd_byte(self.LCD_LINE_3, self.LCD_CMD)
        elif line == 4:
            self.lcd_byte(self.LCD_LINE_4, self.LCD_CMD)    
        for i in range(self.LCD_WIDTH):
            self.lcd_byte(ord(message[i]),self.LCD_CHR)



def lms_time_to_string(lms_time ):
    """convert a time from LMS into a mm:ss time"""
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
    print ("-p <ipPlayer>")
    print ("-w <lcd_width>")
    print ("-l <lcd_address>")

    print ("ipserver like 192.168.1.102")
    print ("player like 192.168.1.115 / default = player n*1") 
    print ("lcd with is 16 or 20 / 16 means 16x2, 20 means 20x4 / default = 20")
    print ("lcd_address is the i2C LCD address like 0x3f (default). Use sudo i2cdetect -y 0") 

    print ("----------------------------------------------------------------")

def main(argv):
    """MAIN LCD MANAGER APP FOR LMS"""
    lmsserver = "127.0.0.1"
    lmsplayer = ""
    lcd_address = "0x3f"
    lcd_w = 20
    verbose = True
    try:
        opts, args = getopt.getopt(argv,"hs:p:w:l",["server=","player=","lcd_width=","lcd_address="])
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
        elif opt in("-w","--lcd_width"):
            lcd_w = int(arg)
        elif opt in("-l","--lcd_address"):
            lcd_address = arg    
           

    myLCD = LCD(int(lcd_address,16), lcd_w)
    #myLCD.lcd_string"1234567890123456",1)
    myLCD.lcd_string("   TVC Audio    ",1)
    myLCD.lcd_string("  LMS LCD INFO  ",2)
    sleep(2)
    myLCD.lcd_string("(C)2017 Renaud  ",1)
    myLCD.lcd_string("Coustellier     ",2)
    sleep(1)
    myLCD.lcd_string("Initializing",1)
    myLCD.lcd_string("Please wait",2)


    sc = Server(hostname=lmsserver, port=9090, username="user", password="password")

    test_con = 1
    test_max = 5

    
    # Server connection
    # Clock mode wating connection
    connected = False
    while connected <> True:
        try:
            sc.connect()
            myLCD.lcd_string("Connecting",1)
            myLCD.lcd_string(lmsserver,2)
            sleep(1)
            connected = True
        except:
            if lcd_w ==16:
                myLCD.lcd_string(" **  Clock **",1)
                myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M:%S'),2)
                sleep(5)
            else:
                myLCD.lcd_string("     ** Clock **",1)
                myLCD.lcd_string(" ",2)
                myLCD.lcd_string(time.strftime('%Y-%m-%d  %H:%M'),3)
                myLCD.lcd_string(" ",4)
                sleep(5)


    #myLCD.lcd_string"1234567890123456",1)
    myLCD.lcd_string("LMS SERVER",1)
    myLCD.lcd_string("LMS v.: %s" % sc.get_version(),2)
    sleep(5)
    
    # Player Connection
    if sc.get_player_count() > 0:
        if verbose==True:
            print ("Players %d" % sc.get_player_count())
            print (sc.get_players(True))
        myLCD.lcd_string("Players cnt= %d" % sc.get_player_count(),2)
        sleep(2)
    else:
        if verbose==True:
            print ("No Player connected")
        
        while sc.get_player_count() == 0:
            myLCD.lcd_string("No player cncted",1)
            myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M'),2)
            sleep(5)
    
    players = []
    players = sc.get_players(True)   
    p = 0

    if lmsplayer <> "":
        if lcd_w == 16:
            for player in players:
                ipPlayer = str(players[p].get_ip_address())
                ipPlayer = ipPlayer[0:ipPlayer.find(":")]
                myLCD.lcd_string("found player",1)
                myLCD.lcd_string(ipPlayer,2)
                print (ipPlayer)
                sleep(1)    
                if ipPlayer == lmsplayer:
                    sq = players[p]
                    break
                p = p + 1
        else:
            for player in players:
                ipPlayer = str(players[p].get_ip_address())
                ipPlayer = ipPlayer[0:ipPlayer.find(":")]
                myLCD.lcd_string("found player",1)
                if p < 4:
                    myLCD.lcd_string(ipPlayer, p+2)
                else:
                    myLCD.lcd_string(ipPlayer,4)
            
                sleep(1)    
                if ipPlayer == lmsplayer:
                    myLCD.lcd_string("-->" + lmsplayer,2)
                    myLCD.lcd_string("connected !",3)
                    myLCD.lcd_string(" ",4)
                    sleep(2)
                    sq = player
                    break
                p = p + 1
    else:
         while True:
            print ("Player autodiscovering...")
            
            players = []
            players = sc.get_players(True)   
            for player in players:
                sq = player
                modePlayer = sq.get_mode()
                if modePlayer == "play":
                    break
                sleep(2)
            if modePlayer == "play":
                ipPlayer = player.get_ip_address()
                print("discovered " + ipPlayer)
                break

    playerName = sq.get_name()
    playerModel = sq.get_model()
    
    if lcd_w == 20:
        myLCD.lcd_string(playerName,3)
        myLCD.lcd_string(playerModel,4)
    sleep(2)
    
    if lcd_w == 16:
        # 16x2 LCD Code
        while True:
            try:
                modePlayer = sq.get_mode()  
                if modePlayer == "pause":
                    myLCD.lcd_string("mode = pause",1)
                    myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M:%S'),2)
                    sleep(2)
                elif modePlayer == "stop":
                    myLCD.lcd_string("     Clock     ",1)
                    myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M'),2)
                    sleep(2)
                    sleep(0.5)
                    # when player is stop, looking for running player...
                    players = []
                    players = sc.get_players(True)   
                    for player in players:
                        sq = player
                        modePlayer = sq.get_mode()
                        if modePlayer == "play":
                            break
                    
                elif modePlayer == "play":
                    trackAlbum = sq.get_track_album()
                    currentTrack = sq.get_track_current_title()
                    trackArtist = sq.get_track_artist()
                    currentVolume = sq.get_volume()
                    
                    print ("")
                    print ("album:" + trackAlbum)
                    print ("artist:" + trackArtist)
                    print ("title:" + currentTrack)

                    myLCD.lcd_string("Alb." + trackAlbum,1)
                    myLCD.lcd_string("Art." + trackArtist,2)
                    sleep(2)
                    myLCD.lcd_string(trackAlbum,1)
                    myLCD.lcd_string(trackArtist,2)
                    
                    td =  "/" + lms_time_to_string(sq.get_track_duration())        
                    ptc = str(sq.playlist_track_count()) 
                    linestatus = 0
                    charOffset = 0
                    while True:
                        linestatus = linestatus + 1
                        volume = (" - Volume %" + str(sq.get_volume()) )
                        #te =  "time " + lms_time_to_string(sq.get_time_elapsed())
                        te = lms_time_to_string(sq.get_time_elapsed()) 
                        te = te + td
                        cti = str(sq.playlist_current_track_index())
                        
                        if len(cti) > 1 and len(ptc) > 1:
                            if linestatus % 4 == 0:
                                te = te + "  /" + ptc
                            else:
                                
                                te = te + "  " + cti + "/"
                        else:
                            te = te + " " + cti + "/" + ptc
                        
                        while currentVolume != sq.get_volume():
                            # Volume
                            currentVolume = sq.get_volume()
                            myLCD.lcd_string("Volume %" + str(currentVolume), 1)    
                            sleep(0.3)
                        if linestatus < 2:
                            myLCD.lcd_string("tle:" + currentTrack, 1)
                            myLCD.lcd_string(te, 2)
                        else: 
                            # Track Name
                            if len(currentTrack) <= lcd_w:
                                # LENGHT is < LCD LCD_WIDTH
                                myLCD.lcd_string(currentTrack, 1)
                            else:
                                # LENGHT is > LCD_WIDTH
                                charOffset = linestatus - 2
                                myLCD.lcd_string(currentTrack[charOffset:], 1) 
                                if linestatus + lcd_w > len(currentTrack):
                                    linestatus = 0       
                            myLCD.lcd_string(te, 2)    
                        if sq.get_track_current_title() != currentTrack or sq.get_mode() !="play" :
                            # change detected
                            myLCD.lcd_string("Track/mode chang", 1)
                            myLCD.lcd_string("pls wait...     ", 2)
                            linestatus = 0
                            break
                        sleep(0.65)
            except:
                print("error -->", sys.exc_info()[0])
                myLCD.lcd_string("Sorry error", 1)
                myLCD.lcd_string(sys.exc_info()[0], 2)
                quit(0)

    else:
        # 20x4 LCD Code
        print ("Power Sate" + str(sq.get_power_state()))
        while True:
            try:
                modePlayer = sq.get_mode()
                if modePlayer == "pause":
                    myLCD.lcd_string(playerName + "=" + modePlayer,1)
                    myLCD.lcd_string(playerModel,2)
                    line3 = "RJ45"
                    ipPlayer = sq.get_ip_address()
                    ipPlayer = ipPlayer[0:ipPlayer.find(":")]
                    if int(sq.get_wifi_signal_strength()) > 1:
                        line3 = "wifi" + str(sq.get_wifi_signal_strength())
                    line3 = line3 + " " + ipPlayer
                    myLCD.lcd_string(line3,3)
                    myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M:%S'),4)
                    sleep(0.5)
                elif modePlayer == "stop":
                    myLCD.lcd_string("       Clock",1)
                    myLCD.lcd_string(" ",2)
                    myLCD.lcd_string(time.strftime('%Y-%m-%d %H:%M'),3)
                    myLCD.lcd_string("  www.tvcaudio.com ",4)
                    sleep(2)
                    # when player mode is stop, looking for another running player...
                    players = []
                    players = sc.get_players(True)   
                    for player in players:
                        sq = player
                        modePlayer = sq.get_mode()
                        if modePlayer == "play":
                            break
                        

                elif modePlayer == "play":
                    trackAlbum = sq.get_track_album()
                    currentTrack = sq.get_track_current_title()
                    trackArtist = sq.get_track_artist()
                    currentVolume = sq.get_volume()
                    if verbose == True:
                        print ("")
                        print ("album:" + trackAlbum)
                        print ("artist:" + trackArtist)
                        print ("title:" + currentTrack)

                    #myLCD.lcd_string(trackArtist,1  )
                    #myLCD.lcd_string(trackAlbum,2)
                    td =  "/" + lms_time_to_string(sq.get_track_duration())        
                    
                    linestatus = 0
                    charOffset = 0
                    
                    while True:
                        linestatus = linestatus + 1
                        volume = (" - Volume %" + str(sq.get_volume()) )
                        te = lms_time_to_string(sq.get_time_elapsed()) 
                        te = te + td
                        te = te + "   " + str(sq.playlist_current_track_index()) + "/" + str(sq.playlist_track_count()) 
                        while currentVolume != sq.get_volume():
                            # Volume
                            currentVolume = sq.get_volume()
                            myLCD.lcd_string("Volume %" + str(currentVolume), 1)    
                            #print (sq.get_rate())
                            print (sq.get_treble())
                            print (sq.get_pitch())
                            sleep(.4)
                        if sq.get_track_current_title() != currentTrack or sq.get_mode() !="play" :
                            # change detected
                            myLCD.lcd_string("Track/mode chang", 1)
                            myLCD.lcd_string("pls wait...     ", 2)
                            break    
                        
                        # Track Name
                        myLCD.lcd_string(trackArtist, 1)
                        myLCD.lcd_string(trackAlbum, 2)
                        #----------------------------
                        if len(currentTrack) <= lcd_w:
                            # LENGHT is < LCD LCD_WIDTH
                            myLCD.lcd_string(currentTrack, 3)
                        else:
                            # LENGHT is > LCD_WIDTH
                            charOffset = linestatus - 1
                            myLCD.lcd_string(currentTrack[charOffset:], 3) 
                            if linestatus + lcd_w > len(currentTrack):
                                linestatus = 0       
                        #myLCD.lcd_string(currentTrack, 3)
                        
                        myLCD.lcd_string(te, 4)
                        sleep(0.5)
            except:
                #if sq.get_power_state():
                print("error -->", sys.exc_info()[0])
                myLCD.lcd_string("error occured", 1)
               

if __name__ == "__main__":
    
    main(sys.argv[1:])        
