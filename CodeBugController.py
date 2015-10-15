#!/usr/bin/env python
# CrumbleController - control Crumble via Scratch

#Copyright (C) 2015 by Simon Walters
# uses libraries copyright (C) 2015 by Joseph Birks that are not licensed for modifcation or re-use outside of this project

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#Last mod 01Jan14


#from codebug_i2c_tether import CodeBug
import codebug_i2c_tether
import time
#import winreg as winreg
import itertools
print ("codebug_i2c_tether.CodeBug()",codebug_i2c_tether.CodeBug())
CB = codebug_i2c_tether.CodeBug()
print ("CB",CB)



class CodeBugController:

    def __init__(self, debug=False):
        self.piRevision = 1
        self.i2cbus = 1
        if self.piRevision == 1:
            self.i2cbus = 0

        #Set some constants and initialise lists
        self.numOfPins = 7 #there are actually 6 but python can't count properly :)

        self.PINPUT = 4
        self.POUTPUT = 1
        self.PPWM = 2
        self.PUNUSED = 8
        self.PSONAR = 16
        self.PULTRA = 32
        self.PSERVOD = 64
        self.PSTEPPER = 128
        self.PCOUNT = 256
        self.PINPUTDOWN = 512
        self.PINPUTNONE = 1024
        self.PPWMMOTOR = 2048
        self.PPWMLED = 4096

        #self.INVERT = False
        self.ledDim = 100

        self.PWMMOTORFREQ = 10

        self.dsSensorId  = ""
        self.senderLoopDelay = 0.2
        self.mFreq = 10
        self.ultraFreq = 1
        self.pFreq = 200




        self.pinUse = [self.PUNUSED] * self.numOfPins
        self.servodPins = None

        self.pinRef = [None] * self.numOfPins
        self.pinCount = [0] * self.numOfPins
        self.countDirection = [1] * self.numOfPins
        self.pinEncoderDiff = [0] * self.numOfPins
        self.encoderStopCounting = [0] * self.numOfPins
        self.pinLastState = [0] * self.numOfPins
        self.encoderTime = [0] * self.numOfPins
        self.encoderTimeDiff = [0.0] * self.numOfPins
        self.gpioLookup = [0] * self.numOfPins
        self.callbackInUse = [False] * self.numOfPins
        self.pinValue = [0] * self.numOfPins
        self.pinInvert = [False] * self.numOfPins
        #print "pinValue" , self.pinValue
        #print "pin Value 3 = ", self.pinValue[3]
        self.pinUltraRef = [None] * self.numOfPins
        self.pinTrigger = [0] * self.numOfPins
        self.pinTriggerName = ["x"] * self.numOfPins
        self.anyTrigger = 0
        self.pinServoValue = [None] * self.numOfPins
        self.gpioMyPinEventDetected = [False] * self.numOfPins
        self.pinTriggerLastState = [0] * self.numOfPins
        self.encoderCallback = 0

        self.pinEventEnabled = True
        self.encoderInUse = 0

        self.nunchuckLevel = 1

        self.capTouch = None
        self.capTouchHelper = None
        self.ADS1015 = None
        self.lightDirection = 0
        self.lightValue = 0
        self.lightInfo = False
        self.autoLink = False
        self.linkPrefix = None

        self.validPins =      [0,1,2,3,4,5]

        #self.gpioLookup = ["a","b","c","d"]

        self.writeTextDelay = 0.1


        #self.ULTRA_IN_USE = [False] * self.PINS
        #self.ultraTotalInUse = 0
        #self.ultraSleep = 1.0
        self.debug = debug
        if self.debug:
            print("sghGC Debug enabled")
        # End init

    #reset pinmode
    def resetPinMode(self):
        test = True
        #print "resetting pin mode"
        # self.stopServod()
        # for pin in self.validPins:
        #     try:
        #         self.pinRef[pin].stop() # stop PWM from running
        #         self.pinRef[pin] = None
        #     except:
        #         pass
        #     self.pinRef[pin] = None #reset pwm flag
        #
        #     try:
        #         GPIO.remove_event_detect(pin) #Stop Any event detection for input and counting
        #     except:
        #         pass
        #
        #     try:
        #         self.callbackInUse[pin] = False  #reset event callback flags
        #     except:
        #         pass
        #
        #     if (self.pinUse[pin] == self.POUTPUT):
        #         GPIO.setup(pin,GPIO.IN)
        #     elif (self.pinUse[pin] == self.PINPUT):
        #         GPIO.setup(pin,GPIO.IN)
        #     elif (self.pinUse[pin] == self.PINPUTDOWN):
        #         GPIO.setup(pin,GPIO.IN)
        #     elif (self.pinUse[pin] == self.PINPUTNONE):
        #         GPIO.setup(pin,GPIO.IN)
        #     elif (self.pinUse[pin] == self.PCOUNT):
        #         GPIO.setup(pin,GPIO.IN)
        #     self.pinUse[pin] = self.PUNUSED
        #     self.pinServoValue[pin] = None
        #
        #     print "reset pin", pin
        #     self.pinValue[pin] = 0
        #     self.pinInvert[pin] = False


    #Procedure to set pin mode for each pin
    def setPinMode(self):
        test = True
        # for pin in self.validPins:
        # #     #print pin
        #     if (self.pinUse[pin] == self.POUTPUT):
        #         print 'setting pin' , pin , ' to out'
        #         if (self.pinInvert[pin] == True):
        #             self.GPIOOutput(pin,1)
        #         else:
        #             GPIO.output(pin,0)
        #         self.pinValue[pin] = 0
        #     elif (self.pinUse[pin] == self.PINPUT):
        #         print 'setting pin' , pin , ' to in with pull up'
        #         GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        #         try:
        #             GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.gpioBoth,bouncetime=50)  # add rising edge detection on a channel
        #         except:
        #             pass
        #     elif (self.pinUse[pin] == self.PINPUTDOWN):
        #         print 'setting pin' , pin , ' to in with pull down'
        #         GPIO.setup(pin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
        #         try:
        #             GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.gpioBoth,bouncetime=50)  # add rising edge detection on a channel
        #         except:
        #             pass
        #     elif (self.pinUse[pin] == self.PINPUTNONE):
        #         print 'setting pin' , pin , ' to in with pull down'
        #         GPIO.setup(pin,GPIO.IN)
        #         try:
        #             GPIO.add_event_detect(pin, GPIO.BOTH, callback=self.gpioBoth,bouncetime=50)  # add rising edge detection on a channel
        #         except:
        #             pass
        #     elif (self.pinUse[pin] == self.PCOUNT):
        #         if self.callbackInUse[pin] == False:
        #             print 'setting pin' , pin , ' as counting pin'
        #             GPIO.setup(pin,GPIO.IN)#,pull_up_down=GPIO.PUD_DOWN)#,pull_up_down=GPIO.PUD_DOWN)
        #             try: # add event callback but use try block just in case its already set
        #                 if self.encoderCallback == 1:
        #                     #GPIO.add_event_detect(pin, GPIO.RISING, callback=self.my_callbackB)#,bouncetime=10)  # add rising edge detection on a channel
        #                     self.callbackInUse[pin] = True
        #                     self.encoderCallback = 2
        #                     if self.debug:
        #                         print "callback B set for pin ", pin
        #
        #                 if self.encoderCallback == 0:
        #                     #GPIO.add_event_detect(pin, GPIO.RISING, callback=self.my_callbackA)#,bouncetime=10)  # add rising edge detection on a channel
        #                     self.callbackInUse[pin] = True
        #                     self.encoderCallback = 1
        #                     if self.debug:
        #                         print "callback A set for pin ", pin
        #
        #             except Exception,e:
        #                 print "Error on event detection setup on pin" ,pin
        #                 print str(e)
        #         else:
        #             print ("Callback already in use")
        #
        # print ("SetPinMode:",self.pinUse)

    def pinRead(self, pin):
        #print "pin",pin ,"set to", self.pinUse[pin]
        #print pin ," being read"
        value = 0
        with CB:
            try:
                value = CB.get_input(pin)
            except Exception as e:
                #print "Some error reading pin" ,pin
                print("Make sure you have plugged your CodeBug into your computer")
                time.sleep(2)
                print(str(e))
                pass
                #raise
            #print value
        return value

    def motor(self, motor,value):
        with CB:
            if motor == 1:
                CB.io.set_motor1(value)
            if motor == 2:
                CB.io.set_motor2(value)

    def output(self, output,value):
        with CB:
            CB.set_leg_io(output,0)
            CB.set_output(output,value)

    def GPIOOutput(self,pin,value):
        output = "A"
        if pin == 2:
            output = "B"
        if pin == 3:
            output = "B"
        if pin == 4:
            output = "D"
        self.output(value,output)
        
    def setPixel(self,x,y,state):
        with CB:
            CB.set_pixel(x, y, state)

    def setRow(self,row,value):
        with CB:
            CB.set_row(row, value)

    def setCol(self,col,value):
        with CB:
            CB.set_col(col, value)

    def clear(self):
        with CB:
            CB.clear()

    def writeText(self, x=0 ,y=0, message="Hello", direction = "right"):
        print (x,y,message,direction)
        with CB:
            CB.write_text(x, y, message, direction)

    def getPixel(self,x,y):
        with CB:
            return(CB.get_pixel(x, y))


    def getRow(self,row):
        with CB:
            return(CB.get_row(row))

    def getCol(self,col):
        with CB:
            return(CB.get_col(col))

    def setLegInput(self, leg):
        with CB:
            CB.set_leg_io(leg,1)





