#original from waveshare customizeed by StSkanta (TechCree) 838375
####https://www.waveshare.com/wiki/Pico-ePaper-5.83-B#Download_Demo_codes

import machine
from machine import Pin
import utime
from machine import I2C
import time
import os
import gc

#from rtc import stu, min
#import temperatur

from machine import Pin, SPI
import framebuf
import utime

###Temperatur abfragen
### Setup Temperaturmessung und Konvertierung
#sensor_temp = machine.ADC(4) 
#conversion_factor = 3.3 / (65535) 
#h = 0
#o = 0
#reading = sensor_temp.read_u16() * conversion_factor
#temperature = round(27 - (reading - 0.706) / 0.001721)
#tempa = temperature
###

# Display resolution
EPD_WIDTH       = 648
EPD_HEIGHT      = 480

RST_PIN         = 12
DC_PIN          = 8
CS_PIN          = 9
BUSY_PIN        = 13

#Test Variable (TEXTE)
vari0 = "# <---"

vari1 = "Raspbi Pico"
vari2 = "Waveshare"
vari3 = "EPD_5in83_B"
vari4 = "EPD_5in83_B"
vari5 = "EPD_5in83_B"
vari6 = "EPD_5in83_B"
vari7 = "EPD_5in83_B"
vari8 = "EPD_5in83_B"
vari9 = "EPD_5in83_B"
vari10 = "EPD_5in83_B"

vari11 = "---> #"

class EPD_5in83_B():
    def __init__(self):
        self.reset_pin = Pin(RST_PIN, Pin.OUT)
        
        self.busy_pin = Pin(BUSY_PIN, Pin.IN, Pin.PULL_UP)
        self.cs_pin = Pin(CS_PIN, Pin.OUT)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        
        self.spi = SPI(1)
        self.spi.init(baudrate=4000_000)
        self.dc_pin = Pin(DC_PIN, Pin.OUT)
        
        self.buffer_black = bytearray(self.height * self.width // 8)
        self.buffer_red = bytearray(self.height * self.width // 8)
        self.imageblack = framebuf.FrameBuffer(self.buffer_black, self.width, self.height, framebuf.MONO_HLSB)
        self.imagered = framebuf.FrameBuffer(self.buffer_red, self.width, self.height, framebuf.MONO_HLSB)
        self.init()

    def digital_write(self, pin, value):
        pin.value(value)

    def digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delaytime):
        utime.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.spi.write(bytearray(data))

    def module_exit(self):
        self.digital_write(self.reset_pin, 0)

    # Hardware reset
    def reset(self):
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50) 
        self.digital_write(self.reset_pin, 0)
        self.delay_ms(2)
        self.digital_write(self.reset_pin, 1)
        self.delay_ms(50)   

    def send_command(self, command):
        self.digital_write(self.dc_pin, 0)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([command])
        self.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte([data])
        self.digital_write(self.cs_pin, 1)
        
    def send_data2(self, data):
        self.digital_write(self.dc_pin, 1)
        self.digital_write(self.cs_pin, 0)
        self.spi_writebyte(data)
        self.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        print("e-Paper busy")
        while(self.digital_read(self.busy_pin) == 0):      #  1: idle, 0: busy
            self.delay_ms(10)
        print("e-Paper busy release")  

    def TurnOnDisplay(self):
        self.send_command(0x12) 
        self.delay_ms(100)
        self.ReadBusy()
        
    def init(self):
        # EPD hardware init start     
        self.reset()
        
        self.send_command(0x01)     #POWER SETTING
        self.send_data (0x07)
        self.send_data (0x07)       #VGH=20V,VGL=-20V
        self.send_data (0x3f)       #VDH=15V
        self.send_data (0x3f)       #VDL=-15V

        self.send_command(0x04) #POWER ON
        self.delay_ms(100)  
        self.ReadBusy()   #waiting for the electronic paper IC to release the idle signal

        self.send_command(0X00)     #PANNEL SETTING
        self.send_data(0x0F)        #KW-3f   KWR-2F    BWROTP 0f   BWOTP 1f

        self.send_command(0x61)     #tres
        self.send_data (0x02)       #source 648
        self.send_data (0x88)
        self.send_data (0x01)       #gate 480
        self.send_data (0xe0)

        self.send_command(0X15)
        self.send_data(0x00)

        self.send_command(0X50)     #VCOM AND DATA INTERVAL SETTING
        self.send_data(0x11)
        self.send_data(0x07)

        self.send_command(0X60)     #TCON SETTING
        self.send_data(0x22)
        # EPD hardware init end
        return 0

    def display(self, imageBlack, imageRed):
        if (imageBlack == None or imageRed == None):
            return    
        self.send_command(0x10) # WRITE_RAM
        self.send_data2(imageBlack)
        self.send_command(0x13) # WRITE_RAM
        self.send_data2(imageRed)
        self.TurnOnDisplay()

    def Clear(self, colorBalck, colorRed):
        self.send_command(0x10) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(colorBalck)
        self.send_command(0x13) # WRITE_RAM
        for j in range(0, self.height):
            for i in range(0, int(self.width / 8)):
                self.send_data(colorRed)
        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x02) # DEEP_SLEEP_MODE
        self.ReadBusy()
        self.send_command(0x07)
        self.send_data(0xa5)
        
        self.delay_ms(2000)
        self.module_exit()

########INHALT##A##########

       
if __name__=='__main__':
    epd = EPD_5in83_B()
    epd.Clear(0xff, 0x00)
    
    ###648x480
    epd.imageblack.fill(0xff)
    epd.imagered.fill(0x00)
    ###
    
    #Displayrand Anfang
    epd.imageblack.text(vari0, 1, 1, 0x00)


    #Mein Text
    epd.imagered.text(vari1, 270, 75, 0xff)
    epd.imagered.text(vari2, 270, 85, 0xff)
    epd.imagered.text(vari2, 270, 95, 0xff)
    epd.imagered.text(vari4, 270, 105, 0xff)
    epd.imagered.text(vari5, 270, 115, 0xff)
    epd.imagered.text(vari6, 270, 125, 0xff)
    epd.imagered.text(vari7, 270, 135, 0xff)
    epd.imagered.text(vari8, 270, 145, 0xff)
    epd.imagered.text(vari9, 270, 155, 0xff)
    epd.imagered.text(vari10, 270, 165, 0xff)
    
    
    #Displyrande Ende
    epd.imageblack.text(vari11, 600, 470, 0x00)
    
    ###

    epd.display(epd.buffer_black, epd.buffer_red)
    epd.delay_ms(6000)
    
    
    
#    epd.Clear(0xff, 0x00)
#    epd.delay_ms(8000)
#    print("sleep")
#    epd.sleep()
