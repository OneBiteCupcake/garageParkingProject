#!/usr/bin/python
# -*- coding: utf-8 -*-
import serial
import time
import os
from BlinkyTape import BlinkyTape
 
 
# Function to read chars from serial input until you get a <CR> or null
# before getting a line, clear the buffer/cache.  We do not want "lagging" data
 
def readlineCR(port):
    rv = ''
    port.reset_input_buffer()
    while True:
        ch = port.read()
        rv += ch
        if ch == '\r' or ch == '':
            return rv
 
# Function to get sensor reading as text, validate & return numeric value in mm
 
def getDist():
    mmdist = 0
    while True:
        response = readlineCR(port)
        if len(response) == 6 and response[0] == 'R':
            mmdist = int(response[1:5])
            return mmdist
     
 
# setup serial port parameters per MaxBotix specs
 
port = serial.Serial(
    '/dev/ttyUSB0',
    baudrate=57600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    writeTimeout=0,
    timeout=10,
    rtscts=False,
    dsrdtr=False,
    xonxoff=False,
    )
 
# Open serial port for read/write
 
print port.isOpen()
print 'Port opened...'
 
# initialize variables
# saymtric = say metric measurement (in mm) else imperial (in inches)
# last = last measurement read - used to determine movement
# inches = used if conversion to imperial units desired
# delta = value in mm to determine motion between readings
# inrange = if closer then this, speak! (1800mm = 6' == 72")
# mmmm[ ] = used to determine median of multiple readings -- filter out noise
 
saymetric = False
last = 0
inches = 0
delta = 2#5#10
inrange = 1800
mmmm = [0, 0, 0]
bb = BlinkyTape('/dev/ttyACM0', 60)
red = (255,0,0)
green = (0,255,0)
yellow = (255,255,0)
blue = (0,0,255)
 
# Loop forever for constant measuring.  Will speak if closer than 6 ft (180 cm)
 
while True:
 
# validate & convert text to numeric value in mm
# filter noise by using median of 3 readings
 
    mmmm[0] = getDist()
    mmmm[1] = getDist()
    mmmm[2] = getDist()
    mmmm.sort()
    mmm = mmmm[1]
 
# only talk if there is movement.  check delta
 
    if abs(last - mmm) > delta:
        inches = int(mmm * 10 / 254)
        print inches #mmm
 
# check distance and use selected units of measure (metric vs. imperial)
 
        if (mmm < inrange):
            if (saymetric):
                pass
                #os.system('pico2wave -w /var/local/pico2wave.wav ' + '"' + str(mmm) + '"'  + ' | aplay -q')
            else:
                #os.system('pico2wave -w /var/local/pico2wave.wav ' + '"' + str(inches) + ' inches"' + ' | aplay -q')
                if inches >= 60:
                    bb.displayColor(*green)
                    #print("green")
                    #for x in range(60):
                    #    bb.sendPixel(0,255,0)#green
                elif inches >= 48 and inches < 60:
                    bb.displayColor(*yellow)
                    #print("yellow")
                    #for x in range(60):
                    #    bb.sendPixel(255,255,0)#yellow
                elif inches < 48:
                    bb.displayColor(*red)
                    #print("red")
                    #for x in range(60):
                    #    bb.sendPixel(255,0,0)#red
                else:
                    bb.displayColor(*blue)
                    #print("blue")
                    #for x in range(60):
                    #    bb.sendPixel(0,0,255)#blue

# save mm value to use in delta motion check
 
        last = mmm
        bb.show()
