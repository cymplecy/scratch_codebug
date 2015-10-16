#!/usr/bin/env python
# ScratchCrumble - control Crumble using Scratch
# Copyright (C) 2013-2015 by Simon Walters based on original code for PiFace by Thomas Preston
# Utilises libraries vm.py and crumble.py copyright 2015 Joseph Birks that are not re-distributable and are not GPL2.

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Version = 'v0.4.000'  #16Oct15
print("Version",Version)
import CodeBugController
import threading
import socket
import time
import sys
import struct
import datetime as dt
import shlex
import os
import math
import re
import logging
import subprocess
#import pygame removed because causing random failures
import random
import queue
#from sgh_cheerlights import CheerLights

#import uinput

#ui = UInput()



sghCT = None #reserve for captouch


def isNumeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def rtnNumeric(value, default):
    try:
        return float(value)
    except ValueError:
        return default


def rtnSign(s):
    try:
        if abs(s) == s:
            return 1
        else:
            return -1
    except ValueError:
        return 0


def removeNonAscii(s):
    return "".join(i for i in s if ord(i) < 128)


def getValue(searchString, dataString):
    outputall_pos = dataString.find((searchString + ' '))
    sensor_value = dataString[(outputall_pos + 1 + len(searchString)):].split()
    return sensor_value[0]


def sign(number): return cmp(number, 0)


def parse_data(dataraw, search_string):
    outputall_pos = dataraw.find(search_string)
    return dataraw[(outputall_pos + 1 + search_string.length):].split()


class MyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ScratchSender(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.scratch_socket = socket
        self.scratch_socket2 = None
        self._stop = threading.Event()
        self.time_last_ping = 0.0
        self.time_last_compass = 0.0
        self.distlist = [0.0, 0.0, 0.0]
        self.sleepTime = 1 # just a dummy value to initialise
        print("Sender Init")

    def stop(self):
        self._stop.set()
        print("Sender Stop Set")

    def stopped(self):
        return self._stop.isSet()

    def broadcast_pin_update(self, pin, value):
        #print ADDON
        #print "sending",pin,value
        #sensor_name = "gpio" + str(GPIO_NUM[pin_index])
        #bcast_str = 'sensor-update "%s" %d' % (sensor_name, value)
        #print 'sending: %s' % bcast_str
        #msgQueue.put(((5,bcast_str)))

        #Normal action is to just send updates to pin values but this can be modified if known addon in use
        #print "change in pin" ,pin
        sensor_name = ["Leg0","Leg1","Leg2","Leg3","ButtonA","ButtonB"][pin]
        sensorValue = value
        #print "sensor name", sensor_name
        if pin > 3:
            sensorValue = "on" if value == 1 else "off"
        bcast_str = '"' + sensor_name + '" ' + str(sensorValue)

        msgQueue.put(((5,"sensor-update " + bcast_str)))
        logging.debug("sensor change put in queue:%s", bcast_str)
        #print pin , sghGC.pinTrigger[pin]
        # if sghGC.pinTrigger[pin] == 1:
        #     #print dt.datetime.now()
        #     print "trigger being sent for:", sensor_name
        #     msgQueue.put((5,'broadcast "Trigger' + sensor_name + '"'))
        #     sghGC.pinTriggerName[pin] = sensor_name
        #     sghGC.pinTrigger[pin] = 2
        #     if sghGC.anyTrigger == 0:
        #         #print "Any trigger broadcast"
        #         msgQueue.put((5,'broadcast "Trigger"'))
        #         sghGC.anyTrigger = 2


    def setsleepTime(self, sleepTime):
        self.sleepTime = sleepTime
        #print("sleeptime:%s", self.sleepTime )


    def xrun(self):
        global firstRun, ADDON, compass, wii
        print(lock)
        # while firstRun:
        # print "first run running"
        #time.sleep(5)
        # set last pin pattern to inverse of current state
        pin_bit_pattern = [0] * len(sghGC.validPins)
        last_bit_pattern = [1] * len(sghGC.validPins)

        lastPinUpdateTime = time.time()
        lastTimeSinceLastSleep = time.time()
        lastTimeSinceMCPAnalogRead = time.time()
        self.sleepTime = 0.5
        tick = 0
        lastADC = [256, 256, 256, 256, 256, 256, 256, 256]
        lastpiAndBash = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

        joyx, joyy, accelx, accely, accelz, button = [0, 0, 0, 0, 0, 0]
        lastAngle = 0

        lastmcpInput = 0
        lastTimeSinceMCPAnalogRead = time.time()
        self.sleepTime = 0.5
        tick = 0
        lastADC = [256, 256, 256, 256, 256, 256, 256, 256]
        lastpiAndBash = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

        joyx, joyy, accelx, accely, accelz, button = [0, 0, 0, 0, 0, 0]
        lastAngle = 0

        lastmcpInput = 0
        while not self.stopped():

            loopTime = time.time() - lastTimeSinceLastSleep
            #print "how many millisecs since last loop", (loopTime * 1000)
            if loopTime < self.sleepTime:
                sleepdelay = self.sleepTime - loopTime
                #print "add in sleep of milliesec:",(sleepdelay) * 1000
                time.sleep(sleepdelay)  # be kind to cpu  :)
                tick += 1
                if tick == sys.maxsize:
                    tick = 0
            else:
                print("looptime took", loopTime)
            lastTimeSinceLastSleep = time.time()

        print("Sender Stopped")

            #time.sleep(2)

        
        
    def run(self):
        global firstRun, ADDON, compass, wii
        print(lock)
        # while firstRun:
        # print "first run running"
        #time.sleep(5)
        # set last pin pattern to inverse of current state
        pin_bit_pattern = [0] * len(sghGC.validPins)
        last_bit_pattern = [1] * len(sghGC.validPins)

        lastPinUpdateTime = time.time()
        lastTimeSinceLastSleep = time.time()
        lastTimeSinceMCPAnalogRead = time.time()
        self.sleepTime = 0.5
        tick = 0
        lastADC = [256, 256, 256, 256, 256, 256, 256, 256]
        lastpiAndBash = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

        joyx, joyy, accelx, accely, accelz, button = [0, 0, 0, 0, 0, 0]
        lastAngle = 0

        lastmcpInput = 0


        while not self.stopped():

            loopTime = time.time() - lastTimeSinceLastSleep
            #print "how many millisecs since last loop", (loopTime * 1000)
            if loopTime < self.sleepTime:
                sleepdelay = self.sleepTime - loopTime
                #print "add in sleep of milliesec:",(sleepdelay) * 1000
                time.sleep(sleepdelay)  # be kind to cpu  :)
                tick += 1
                if tick == sys.maxsize:
                    tick = 0
            else:
                print("looptime took", loopTime)
            lastTimeSinceLastSleep = time.time()

            #print "before lock"
            with lock:
                for listIndex in range(len(sghGC.validPins)):
                    pin = sghGC.validPins[listIndex]
                    pin_bit_pattern[listIndex] = 0
                    if (sghGC.pinUse[pin] in [sghGC.PINPUT, sghGC.PINPUTNONE, sghGC.PINPUTDOWN]):
                        #logging.debug("Checking event on pin:%s", pin )
                        #pinEvent = sghGC.pinEvent(pin)
                        pinValue = sghGC.pinRead(pin)
                        #print pin,pinValue
                        pin_bit_pattern[listIndex] = pinValue
                        # if pinEvent:
                        #     logging.debug(" ")
                        #     logging.debug("pinEvent Detected on pin:%s", pin)
                        #     #logging.debug("before updating pin patterm,last pattern :",pin_bit_pattern[listIndex],last_bit_pattern[listIndex] )
                        #     #logging.debug("afte uipdating pin patterm:",pin_bit_pattern[listIndex] )
                        #     if pin_bit_pattern[listIndex] == last_bit_pattern[listIndex]:
                        #         logging.debug("pinEvent but pin state the same as before...")
                        #         #pin_bit_pattern[listIndex] = 1 - pin_bit_pattern[listIndex] #change pin pattern - warning pin_bit_pattern now has !pin state
                        #     #logging.debug("after checking states pin patterm,last pattern:",pin_bit_pattern[listIndex],last_bit_pattern[listIndex])
                        #
                        #     if sghGC.pinTrigger[pin] == 0:
                        #         sghGC.pinTrigger[pin] = 1
                        #         #print " "
                        #         #print "pin trigged:",pin,sghGC.pinTrigger[pin]
                        #         #print " "
                        #     time.sleep(0)




                    #print wii

            # if there is a change in the input pins
            for listIndex in range(len(sghGC.validPins)):
                #print "listIndex", listIndex
                pin = sghGC.validPins[listIndex]
                if (pin_bit_pattern[listIndex] != last_bit_pattern[listIndex]) or sghGC.pinTrigger[pin] == 1:
                    logging.debug("Change or triger detected in pin:%s value:%s, trigger val:%s", pin,
                                  pin_bit_pattern[listIndex], sghGC.pinTrigger[pin])
                    if (sghGC.pinUse[pin] in [sghGC.PINPUT, sghGC.PINPUTNONE, sghGC.PINPUTDOWN]):
                        #print pin , pin_value
                        self.broadcast_pin_update(pin, pin_bit_pattern[listIndex])
                        time.sleep(0.05)  # just to give Scratch a better chance to react to event

            last_bit_pattern = list(pin_bit_pattern)
            #print ("last:%s",last_bit_pattern)
            #print ("this:%s",pin_bit_pattern)


            if (time.time() - lastPinUpdateTime) > 3:  #This is to force the pin names to be read out even if they don't change
                print("Heartbeat", time.ctime(time.time()))
                logging.debug("  ")
                logging.debug("Forced heartbeat sensor update")
                lastPinUpdateTime = time.time()
                with lock: #added in ScratchCrumble to see if issue is with locking
                    for listIndex in range(len(sghGC.validPins)):
                        pin = sghGC.validPins[listIndex]
                        if (sghGC.pinUse[pin] in [sghGC.PINPUT, sghGC.PINPUTNONE, sghGC.PINPUTDOWN]):
                            pin_bit_pattern[listIndex] = sghGC.pinRead(pin)
                            self.broadcast_pin_update(pin, pin_bit_pattern[listIndex])
                            #print "bits", pin_bit_pattern



        print("Sender Stopped")

            #time.sleep(2)


class ScratchListener(threading.Thread):
    def __init__(self, socket):
        print("Listiner init")
        threading.Thread.__init__(self)
        self.scratch_socket = socket
        self.scratch_socket2 = None
        self._stop = threading.Event()
        self.dataraw = ''
        self.value = None
        self.valueNumeric = None
        self.valueIsNumeric = None
        self.OnOrOff = None
        self.searchPos = 0
        self.encoderDiff = 0
        self.turnSpeed = 40
        self.turnSpeedAdj = 0

        self.matrixX = 0
        self.matrixY = 0
        self.matrixUse = 64
        self.matrixColour = 'FFFFFF'
        self.matrixRed = 255
        self.matrixGreen = 255
        self.matrixBlue = 255
        self.matrixMult = 1
        self.matrixLimit = 1
        self.matrixRangemax = 8
        self.arm = None
        self.carryOn = True
        self.carryOnInUse = False


    def getValue(self, searchString):
        outputall_pos = self.dataraw.find((searchString + ' '))
        sensor_value = self.dataraw[(outputall_pos + 1 + len(searchString)):].split()
        try:
            return sensor_value[0]
        except IndexError:
            return ""

    # Find pos of searchStr - must be preceded by a deself.matrixLimiting  space to be found
    def bFind(self, searchStr):
        #print "looking in" ,self.dataraw , "for" , searchStr
        self.searchPos = self.dataraw.find(' ' + searchStr) + 1
        #time.sleep(0.1)
        #if (' '+searchStr in self.dataraw):
        #print "Found"
        return (' ' + searchStr in self.dataraw)

    def bFindOn(self, searchStr):
        return (self.bFind(searchStr + 'on ') or self.bFind(searchStr + 'high ')  or self.bFind(searchStr + 'hi ') or self.bFind(searchStr + '1 '))

    def bFindOff(self, searchStr):
        return (self.bFind(searchStr + 'off ') or self.bFind(searchStr + 'low ')  or self.bFind(searchStr + 'lo ') or self.bFind(searchStr + '0 '))

    def bFindOnOff(self, searchStr):
        #print "searching for" ,searchStr
        self.OnOrOff = None
        if (self.bFind(searchStr + 'on ') or self.bFind(searchStr + 'high ')   or self.bFind(searchStr + 'hi ') or self.bFind(
                    searchStr + '1 ') or self.bFind(searchStr + 'true ')):
            self.OnOrOff = 1
            self.valueNumeric = 1
            self.value = "on"
            return True
        elif (self.bFind(searchStr + 'off ') or self.bFind(searchStr + 'low ')  or self.bFind(searchStr + 'lo ') or self.bFind(
                    searchStr + '0 ') or self.bFind(searchStr + 'false ')):
            self.OnOrOff = 0
            self.valueNumeric = 0o1
            self.value = "off"
            return True
        else:
            return False


    def bCheckAll(self, default=True, pinList=None):
        if self.bFindOnOff('all'):
            if default:
                pinList = sghGC.validPins
            for pin in pinList:
                #print pin
                if sghGC.pinUse[pin] in [sghGC.POUTPUT, sghGC.PPWM, sghGC.PPWMMOTOR]:
                    #print pin
                    sghGC.pinUpdate(pin, self.OnOrOff)

    def bPinCheck(self, pinList):
        for pin in pinList:
            logging.debug("bPinCheck:%s", pin)
            if self.bFindOnOff('pin' + str(pin)):
                sghGC.pinUpdate(pin, self.OnOrOff)
            if self.bFindOnOff('gpio' + str(sghGC.gpioLookup[pin])):
                sghGC.pinUpdate(pin, self.OnOrOff)
            if self.bFindValue('power' + str(pin)):
                print(pin, self.value)
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pin, self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(pin, 0, type="pwm")


    def bLEDCheck(self, ledList):
        for led in range(1, (1 + len(ledList))):  # loop thru led numbers
            if self.bFindOnOff('led' + str(led)):
                sghGC.pinUpdate(ledList[led - 1], self.OnOrOff)

    def bListCheck(self, pinList, nameList):
        for loop in range(0, len(pinList)):  # loop thru list
            #print str(nameList[loop]) , pinList[loop]
            if self.bFindOnOff(str(nameList[loop])):
                #print str(nameList[loop]) , "found"
                sghGC.pinUpdate(pinList[loop], self.OnOrOff)

            if self.bFindValue('power' + str(nameList[loop]) + ","):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pinList[loop], self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(pinList[loop], 0, type="pwm")

    def bListCheckPowerOnly(self, pinList, nameList):
        for loop in range(0, len(pinList)):  # loop thru list
            if self.bFindValue('power' + str(nameList[loop]) + ","):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pinList[loop], self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(pinList[loop], 0, type="pwm")

    def bFindValue(self, searchStr, searchSuffix=''):
        #logging.debug("Searching for:%s",searchStr )
        #return the value of the charachters following the searchstr as float if possible
        #If not then try to return string
        #If not then return ""
        self.value = None
        self.valueNumeric = None
        self.valueIsNumeric = False

        if self.bFind(searchStr):
            if searchSuffix == '':
                #print "$$$" + self.dataraw + "$$$"
                #print "search" , searchStr
                #print "pos", self.searchPos
                #print "svalue",(self.dataraw[(self.searchPos + len(searchStr)):] + "   ")
                #print "bfind",(self.dataraw[(self.searchPos + len(searchStr)):] + "    ").split()
                self.value = (self.dataraw[(self.searchPos + len(searchStr)):] + "   ").strip()
                if len(self.value) > 0:
                    self.value = self.value.split()[0]
                #print "1 s value",self.value
                #print self.value
                if isNumeric(self.value):
                    self.valueNumeric = float(self.value)
                    self.valueIsNumeric = True
                    #print "numeric" , self.valueNumeric
                return True
            else:
                self.value = (self.dataraw[(self.searchPos + len(searchStr)):] + "   ").strip()
                if len(self.value) > 0:
                    self.value = self.value.split()[0]
                if self.value.endswith(searchSuffix):
                    self.value = (self.value[:-len(searchSuffix)]).strip()
                    #print "2 s value",self.value
                    #print self.value
                    if isNumeric(self.value):
                        self.valueNumeric = float(self.value)
                        self.valueIsNumeric = True
                        #print "numeric" , self.valueNumeric
                    return True
                else:
                    return False
        else:
            return False

    def bLEDPowerCheck(self, ledList):
        for led in range(1, (1 + len(ledList))):  # loop thru led numbers
            #print "power" +str(led) + ","
            if self.bFindValue('power' + str(led) + ","):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(ledList[led - 1], self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(ledList[led - 1], 0, type="pwm")

    def vFind(self, searchStr):
        return ((' ' + searchStr + ' ') in self.dataraw)

    def vFindOn(self, searchStr):
        return (self.vFind(searchStr + 'on') or self.vFind(searchStr + 'high') or self.vFind(searchStr + '1'))

    def vFindOff(self, searchStr):
        return (self.vFind(searchStr + 'off') or self.vFind(searchStr + 'low') or self.vFind(searchStr + '0'))

    def vFindOnOff(self, searchStr):
        self.value = None
        self.valueNumeric = None
        self.valueIsNumeric = False
        self.OnOrOff = None
        if self.vFind(searchStr):

            self.value = self.getValue(searchStr)
            if str(self.value) in ["high", "on", "1"]:
                self.valueNumeric = 1
                self.OnOrOff = 1
            else:
                self.valueNumeric = 0
                self.OnOrOff = 0
            return True
        else:
            return False

    def vFindValue(self, searchStr):
        #print "searching for ", searchStr
        self.value = None
        self.valueNumeric = None
        self.valueIsNumeric = False
        if self.vFind(searchStr):
            #print "found"
            self.value = self.getValue(searchStr)
            #print self.value
            if isNumeric(self.value):
                self.valueNumeric = float(self.value)
                self.valueIsNumeric = True
                #print "numeric" , self.valueNumeric
            return True
        else:
            return False

    def vAllCheck(self, searchStr):
        if self.vFindOnOff(searchStr):
            for pin in sghGC.validPins:
                if sghGC.pinUse[pin] in [sghGC.POUTPUT, sghGC.PPWM, sghGC.PPWMMOTOR]:
                    sghGC.pinUpdate(pin, self.valueNumeric)

    def vPinCheck(self):
        for pin in sghGC.validPins:
            #print "checking pin" ,pin
            if self.vFindValue('pin' + str(pin)):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pin, self.valueNumeric)
                else:
                    sghGC.pinUpdate(pin, 0)

            if self.vFindValue('power' + str(pin)):
                #print pin , "found"
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pin, self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(pin, 0, type="pwm")

            if self.vFindValue('motor' + str(pin)):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pin, self.valueNumeric, type="pwmmotor")
                else:
                    sghGC.pinUpdate(pin, 0, type="pwmmotor")

            if self.vFindValue('gpio' + str(sghGC.gpioLookup[pin])):
                logging.debug("gpio lookup %s", str(sghGC.gpioLookup[pin]))
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pin, self.valueNumeric)
                else:
                    sghGC.pinUpdate(pin, 0)
                    #time.sleep(1)

            if self.vFindValue('powergpio' + str(sghGC.gpioLookup[pin])):
                logging.debug("pin %s", pin)
                logging.debug("gpiopower lookup %s", str(sghGC.gpioLookup[pin]))
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pin, self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(pin, 0, type="pwm")

    def vLEDCheck(self, ledList):
        for led in range(1, (1 + len(ledList))):  # loop thru led numbers
            if self.vFindOnOff('led' + str(led)):
                sghGC.pinUpdate(ledList[led - 1], self.OnOrOff)
                #logging.debug("pin %s %s",ledList[led - 1],self.OnOrOff )

            if self.vFindValue('power' + str(led)):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(ledList[led - 1], self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(ledList[led - 1], 0, type="pwm")


    def vListCheck(self, pinList, nameList):
        for loop in range(0, len(pinList)):  # loop thru pinlist numbers
            if self.vFindOnOff(str(nameList[loop])):
                sghGC.pinUpdate(pinList[loop], self.OnOrOff)

            if self.vFindValue('power' + str(nameList[loop])):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pinList[loop], self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(pinList[loop], 0, type="pwm")
            if self.vFindValue('motor' + str(nameList[loop])):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pinList[loop], self.valueNumeric, type="pwmmotor")
                else:
                    sghGC.pinUpdate(pinList[loop], 0, type="pwmmotor")

    def vListCheckPowerOnly(self, pinList, nameList):
        for loop in range(0, len(pinList)):  # loop thru pinlist numbers
            if self.vFindValue('power' + str(nameList[loop])):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pinList[loop], self.valueNumeric, type="pwm")
                else:
                    sghGC.pinUpdate(pinList[loop], 0, type="pwm")

    def vListCheckMotorOnly(self, pinList, nameList):
        for loop in range(0, len(pinList)):  # loop thru pinlist numbers
            if self.vFindValue('motor' + str(nameList[loop])):
                if self.valueIsNumeric:
                    sghGC.pinUpdate(pinList[loop], self.valueNumeric, type="pwmmotor")
                else:
                    sghGC.pinUpdate(pinList[loop], 0, type="pwmmotor")

    def stop(self):
        self._stop.set()
        print("Listener Stop Set")

    def stopped(self):
        return self._stop.isSet()

    def beep(self, pin, freq, duration):
        logging.debug("Freq:%s", freq)
        if sghGC.pinUse != sghGC.PPWM:  # Checks use of pin if not PWM mode then
            sghGC.pinUpdate(pin, 0, "pwm")  #Set pin to PWM mode
        startCount = time.time()  #Get current time
        sghGC.pinFreq(pin, freq)  # Set freq used for PWM cycle
        sghGC.pinUpdate(pin, 50, "pwm")  # Set duty cycle to 50% to produce square wave
        while (time.time() - startCount) < (duration * 1.0):  # Wait until duration has passed
            time.sleep(0.01)
        sghGC.pinUpdate(pin, 0, "pwm")  #Turn pin off


    # noinspection PyPep8Naming
    def run(self):
        global firstRun, cycle_trace, step_delay, stepType, INVERT, \
            Ultra, ultraTotalInUse, piglow, PiGlow_Brightness, compass, ADDON, \
            meVertical, meHorizontal, meDistance, host



        #firstRun = True #Used for testing in overcoming Scratch "bug/feature"
        firstRunData = ''
        anyAddOns = False
        ADDON = ""
        #ultraThread = None

        #semi global variables used for servos in PiRoCon
        panoffset = 0
        tiltoffset = 0
        pan = 0
        tilt = 0
        steppersInUse = None
        beepDuration = 0.5
        beepNote = 60
        self.arm = None
        meHorizontal = 0
        meDistance = 100
        meVertical = 50
        tcolours = None  # set tcolours to None so it can be detected later
        pnblcd = None
        cheerList = None
        UH = None

        with lock:
            print("set pins standard")
            #print "valid",sghGC.validPins
            for pin in sghGC.validPins:
                sghGC.pinUse[pin] = sghGC.PINPUT
                #print pin
            sghGC.setPinMode()


            #This is main listening routine
        lcount = 0
        dataPrevious = b""
        debugLogging = False

        listenLoopTime = time.time() + 10000
        datawithCAPS = ''
        #This is the main loop that listens for messages from Scratch and sends appropriate commands off to various routines
        while not self.stopped():

            #print "ListenLoopTime",listenLoopTime-time.time()
            listenLoopTime = time.time()
            #lcount += 1
            #print lcount
            try:
                #print "try reading socket"
                BUFFER_SIZE = 512  # This size will accomdate normal Scratch Control 'droid app sensor updates
                data = self.scratch_socket.recv( BUFFER_SIZE).decode("utf-8")   # get the data from the socket plus any data not yet processed
                logging.debug("datalen: %s", len(data))
                logging.debug("RAW: %s", data)
                print (type(data))

                if "send-vars" in data:
                    #Reset if New project detected from Scratch
                    #tell outer loop that Scratch has disconnected
                    if cycle_trace == 'running':
                        cycle_trace = 'disconnected'
                        print("cycle_trace has changed to", cycle_trace)
                        break

                if len(data) > 0:  # Connection still valid so process the data received

                    dataIn = data
                    # print "datain", dataIn

                    # if sghGC.autoLink:
                    #     print "autolink"
                    #     print self.scratch_socket2
                    #     if self.scratch_socket2 is not None:
                    #         print "dataIn",dataIn
                    #         dataOut = dataIn.replace(' "',' "#' + sghGC.linkPrefix + '#')
                    #         print "sent", dataOut
                    #         self.scratch_socket2.send(dataOut)

                    datawithCAPS = data
                    #dataOut = ""
                    dataList = []  # used to hold series of broadcasts or sensor updates
                    dataPrefix = ""  # data to be re-added onto front of incoming data
                    while len(dataIn) > 0:  # loop thru data
                        if len(dataIn) < 4:  #If whole length not received then break out of loop
                            #print "<4 chrs received"
                            dataPrevious = dataIn  # store data and tag it onto next data read
                            break
                        sizeInfo = dataIn[0:4].encode('utf-8')
                        size = struct.unpack(">L", bytes(sizeInfo))[0]  # get size of Scratch msg
                        #print "size:", size
                        if size > 0:
                            #print dataIn[4:size + 4]
                            dataMsg = dataIn[4:size + 4].lower()  # turn msg into lower case
                            #print "msg:",dataMsg
                            if len(dataMsg) < size:  # if msg recieved is too small
                                #print "half msg found"
                                #print size, len(dataMsg)
                                dataPrevious = dataIn  # store data and tag it onto next data read
                                break

                            if len(dataMsg) == size:  # if msg recieved is correct
                                if "alloff" in dataMsg:
                                    allSplit = dataMsg.find("alloff")
                                    logging.debug("not sure why this code is here Whole message:%s", dataIn)

                            dataPrevious = ""  # no data needs tagging to next read
                            if ("alloff" in dataMsg) or ("allon" in dataMsg):
                                dataList.append(dataMsg)
                            else:
                                if dataMsg[0:2] == "br":  # removed redundant "broadcast" and "sensor-update" txt
                                    if dataPrefix == "br":
                                        dataList[-1] = dataList[-1] + " " + dataMsg[10:]
                                    else:
                                        dataList.append(dataMsg)
                                        dataPrefix = "br"
                                else:
                                    if dataPrefix == "se":
                                        dataList[-1] += dataMsg[13:] #changr from 10 to 13
                                    else:
                                        dataList.append(dataMsg)
                                        dataPrefix = "se"

                            dataIn = dataIn[size + 4:]  # cut data down that's been processed

                            #print "previous:", dataPrevious



                #print 'Cycle trace' , cycle_trace
                if len(data) == 0:
                    #This is due to client disconnecting or user loading new Scratch program so temp disconnect
                    #I'd like the program to retry connecting to the client
                    #tell outer loop that Scratch has disconnected
                    if cycle_trace == 'running':
                        cycle_trace = 'disconnected'
                        print("cycle_trace has changed to", cycle_trace)
                        break

            except (KeyboardInterrupt, SystemExit):
                print("reraise error")
                raise
            except socket.timeout:
                #print "No data received: socket timeout"
                continue
            except IOError as e:
                print(e.errno)
                print(e)
                if e.errno == 10054:
                    cycle_trace = 'disconnected'
                    print("resetting connection")
                    break
                else:
                    print("Unexpected error occured with receiving data")
                    continue
            #except:
            #    print("Unexpected error occured with receiving data")
            #    continue
            #At this point dataList[] contains a series of strings either broadcast or sensor-updates
            #print "data being processed:" , dataraw
            #This section is only enabled if flag set - I am in 2 minds as to whether to use it or not!
            #if (firstRun == True) or (anyAddOns == False):
            #print
            #logging.debug("dataList: %s",dataList)
            #print
            #print
            #print "old datalist" , dataList

            if any("move" in s for s in dataList) or any("turn" in s for s in dataList):# or any("cheerlight" in s for s in dataList):
                #print "move/turn found in dataList so going to expandList"

                newList = []
                for item in dataList:
                    #print "item" , item
                    if "sensor-update" in item:
                        newList.append(item)
                    if "broadcast" in item:
                        bList = shlex.split(item)  #item.split(" ")
                        for bItem in bList[1:]:
                            newList.append('broadcast "' + bItem + '"')
                dataList = newList
                #print "new dataList" ,dataList

            #print "GPIOPLus" , GPIOPlus
            #print "dataList to be processed", dataList
            for dataItem in dataList:
                #print dataItem
                #dataraw = ' '.join([item.replace(' ','') for item in shlex.split(dataItem)])
                dataraw = ' '
                #print "CAPS", datawithCAPS
                for item in shlex.split(dataItem):
                    #print "item in space remover" ,item
                    if item[0:4] == 'line':
                        origpos = datawithCAPS.lower().find(item)
                        item = datawithCAPS[origpos:origpos + len(item)]
                        item = 'line' + item[4:].strip()
                        item = item[0:5] + item[5:].lstrip()
                        dataraw = dataraw + ''.join(item.replace(' ', chr(254))) + ' '
                    else:
                        dataraw = dataraw + ''.join(item.replace(' ', '')) + ' '
                self.dataraw = dataraw

                logging.debug("processing dataItems: %s", self.dataraw)
                #print "Loop processing"
                #print dataItem, " has been converted to " ,self.dataraw
                #print
                if 'sensor-update' in self.dataraw:
                    #print "this data ignored" , dataraw
                    firstRunData = self.dataraw
                    #dataraw = ''
                    #firstRun = False
                    if self.vFindValue("autostart"):
                        if self.value == "true":
                            print("Autostart GreenFlag event")
                            msgQueue.put((5,"broadcast Scratch-StartClicked"))
                            time.sleep(1)
                            #fred = subprocess.Popen(['xdotool', 'getactivewindow', 'key', 'Return'])
                            #with open('info.txt', "w") as outfile:
                            output = subprocess.Popen(
                                "xwininfo -tree -root | grep squeak | awk '{print $5}' | tr 'x' ',' | tr '+' ','",
                                shell=True, stdout=subprocess.PIPE).communicate()
                            #fred = subprocess.call(['xwininfo','-tree','-root','|','grep','squeak'], stdout = outfile)##'|', 'awk', "'{print $5}'", '|', 'tr', "'x'" ,"','", '|' ,'tr' ,"'+'", "','"
                            # sizes = output[0][0:-1].split(',')
                            # print sizes
                            # xmid = (int(sizes[0]) + int(sizes[2]))/2
                            # ymid = (int(sizes[1]) + int(sizes[3]))/2
                            # print "sizes" ,sizes
                            # fred = subprocess.Popen(['xdotool', 'mousemove', str(xmid), str(ymid)]).wait()
                            # fred = subprocess.Popen(['xdotool', 'click', '1',]).wait()
                            # fred = subprocess.Popen(['xdotool', 'key', 'Return'])
                            # #print "fred",fred



                    if self.vFindValue("sghdebug"):
                        if (self.value == "1") and (debugLogging == False):
                            logging.getLogger().setLevel(logging.DEBUG)
                            debugLogging = True
                        if (self.value == "0") and (debugLogging == True):
                            logging.getLogger().setLevel(logging.INFO)
                            debugLogging = False

                    if self.vFindValue("bright"):
                        sghGC.ledDim = int(self.valueNumeric) if self.valueIsNumeric else 20
                        PiGlow_Brightness = sghGC.ledDim
                        bcast_str = 'sensor-update "%s" %d' % ('bright', sghGC.ledDim)
                        #print 'sending: %s' % bcast_str
                        msgQueue.put((5,bcast_str))


                    pinsoraddon = None
                    if self.vFindValue("setpins"):
                        setupValue = self.value
                        pinsoraddon = "pins"
                    if self.vFindValue("addon"):
                        setupValue = self.value
                        pinsoraddon = "addon"

                    if pinsoraddon is not None:
                        ADDON = setupValue
                        print((ADDON, " declared"))

                        with lock:
                            for pin in sghGC.validPins:
                                if (sghGC.pinUse[pin] in [sghGC.PINPUT, sghGC.PINPUTNONE, sghGC.PINPUTDOWN]):
                                    sghGC.pinTriggerLastState[pin] = sghGC.pinRead(pin)
                                    print("pinTriggerLastState", pin, sghGC.pinTriggerLastState[pin])



                                # if (firstRun == True) and (anyAddOns == False): # if no addon found in firstrun then assume default configuration
                                # with lock:
                                # print "no AddOns Declared"
                                # sghGC.pinUse[11] = sghGC.POUTPUT
                                # sghGC.pinUse[12] = sghGC.POUTPUT
                                # sghGC.pinUse[13] = sghGC.POUTPUT
                                # sghGC.pinUse[15] = sghGC.POUTPUT
                                # sghGC.pinUse[16] = sghGC.POUTPUT
                                # sghGC.pinUse[18] = sghGC.POUTPUT
                                # sghGC.pinUse[7]  = sghGC.PINPUT
                                # sghGC.pinUse[22] = sghGC.PINPUT
                                # sghGC.setPinMode()

                                # firstRun = False


                #If outputs need  inverting (7 segment common anode needs it - PiRingo etc)

                if self.bFind("invert"):  #update pin count values
                    if self.bFindOnOff('invert'):
                        print("global invert set")
                        for pin in sghGC.validPins:  #loop thru all pins
                            sghGC.pinInvert[pin] = self.OnOrOff
                    else:
                        for pin in sghGC.validPins:  #loop thru all pins
                            if self.bFindOnOff('invert' + str(pin)):
                                sghGC.pinInvert[pin] = self.OnOrOff
                                print("invert status pin", pin, "is", sghGC.pinInvert[pin])

                #Change pins from input to output if more needed
                if self.bFind('config'):
                    with lock:
                        for pin in sghGC.validPins:
                            #print "checking pin" ,pin
                            if self.bFindValue('config' + str(pin)):
                                if self.value == "in":
                                    sghGC.pinUse[pin] = sghGC.PINPUT
                                if self.value == "inpulldown":
                                    sghGC.pinUse[pin] = sghGC.PINPUTDOWN
                                if self.value == "inpullnone":
                                    sghGC.pinUse[pin] = sghGC.PINPUTNONE

                        sghGC.setPinMode()
                        ### Check for AddOn boards being declared

                #Listen for Variable changes
                if 'sensor-update' in self.dataraw:

                    motorList = [['motor1', 1], ['motor2', 2]]
                    for listLoop in range(0, 2):
                        if self.vFindValue(motorList[listLoop][0]):
                            with lock:
                                if self.valueIsNumeric:
                                    CrumCon.motor(motorList[listLoop][1],int(self.valueNumeric))



                    if self.bFindValue('servo'):
                            print("servo")
                            for pin in sghGC.validPins:
                                if self.vFindValue('servo' + str(pin)):
                                    svalue = int(self.valueNumeric) if self.valueIsNumeric else -150
                                    svalue = (svalue + 150)
                                    sghGC.pinServod(pin, svalue)


                    #Use bit pattern to control ports
                    if self.vFindValue('pinpattern'):
                        if "pitt" in ADDON:
                            bit_pattern = ('00000000' + self.value)[-8:]
                            print('bit_pattern %s' % bit_pattern)
                            j = 0
                            for pin in [8, 10, 12, 16, 18, 22, 24, 26]:
                                #print "pin" , bit_pattern[-(j+1)]
                                if bit_pattern[-(j + 1)] == '0':
                                    sghGC.pinUpdate(pin, 0)
                                else:
                                    sghGC.pinUpdate(pin, 1)
                                j += 1
                        else:
                            svalue = self.value
                            bit_pattern = ('0000000000000000000000000000000000000000' + svalue)[-sghGC.numOfPins:]
                            j = 0
                            #onSense = '1' if sghGC.INVERT else '0' # change to look for 0 if invert on
                            onSense = '0'
                            for pin in sghGC.validPins:
                                if (sghGC.pinUse[pin] == sghGC.POUTPUT):
                                    #print "pin" , bit_pattern[-(j+1)]
                                    if bit_pattern[-(j + 1)] == onSense:
                                        sghGC.pinUpdate(pin, 0)
                                    else:
                                        sghGC.pinUpdate(pin, 1)
                                    j += 1


                                    ### Check for Broadcast type messages being received
                #print "loggin level",debugLogging
                if (debugLogging == False):
                    logging.getLogger().setLevel(logging.INFO)

                if 'broadcast' in self.dataraw:

                    #print 'broadcast:' , self.dataraw
                    #print "split",  self.dataraw.split(" ")
                    if sghGC.autoLink:
                        for item in self.dataraw.split(" "):
                            if (item != "") and (item != "broadcast") and (item[0] != "#"):
                                #print item
                                if sghGC.linkPrefix is not None:
                                    dataOut = 'broadcast "' + '#' + sghGC.linkPrefix + '#' + item  + '"'
                                else:
                                    dataOut = 'broadcast "' + '#' + 'other' + '#' + item  + '"'
                                #print dataOut
                                n = len(dataOut)
                                b = (chr((n >> 24) & 0xFF)) + (chr((n >> 16) & 0xFF)) + (chr((n >> 8) & 0xFF)) + (
                                    chr(n & 0xFF))

                                if self.scratch_socket2 is not None:
                                    self.scratch_socket2.send(b + dataOut)
                                    print("auto dataOut Sent", dataOut)

                    if self.bFindValue("qmsg"):
                        msgQueue.put((5,self.value))
                        #print "queue len", len(msgQueue)

                    #if self.bFindValue("hardrestart"):
                    #    os.execv(__file__, sys.argv)


                    if self.bFindValue("setpins"):
                        logging.debug("SetPins broadcast found")
                        logging.debug("SetPins value len %d", len(self.value))
                        logging.debug("SetPins value %s", self.value)

                        if len(self.value) == 0:
                            with lock:

                                for pin in sghGC.validPins:
                                    sghGC.pinUse[pin] = sghGC.PINPUTDOWN
                                sghGC.pinUse[11] = sghGC.POUTPUT
                                sghGC.pinUse[12] = sghGC.POUTPUT
                                sghGC.pinUse[13] = sghGC.POUTPUT
                                sghGC.pinUse[15] = sghGC.POUTPUT
                                sghGC.pinUse[16] = sghGC.POUTPUT
                                sghGC.pinUse[18] = sghGC.POUTPUT
                                #sghGC.pinUse[22] = sghGC.PINPUT
                                #sghGC.pinUse[7] = sghGC.PINPUT
                                sghGC.setPinMode()
                                anyAddOns = True

                        elif self.value == "low":
                            with lock:
                                print("set pins to input with pulldown low")
                                for pin in sghGC.validPins:
                                    sghGC.pinUse[pin] = sghGC.PINPUTDOWN
                                #sghGC.pinUse[3] = sghGC.PUNUSED
                                #sghGC.pinUse[5] = sghGC.PUNUSED
                                sghGC.setPinMode()
                                anyAddOns = True

                        elif self.value == "high":
                            with lock:
                                print("set pins to input with pull ups")
                                for pin in sghGC.validPins:
                                    sghGC.pinUse[pin] = sghGC.PINPUT
                                #sghGC.pinUse[3] = sghGC.PUNUSED
                                #sghGC.pinUse[5] = sghGC.PUNUSED
                                sghGC.setPinMode()
                                anyAddOns = True

                        elif self.value == "none":
                            with lock:
                                print("set pins to input with no pullups")
                                for pin in sghGC.validPins:
                                    sghGC.pinUse[pin] = sghGC.PINPUTNONE
                                #sghGC.pinUse[3] = sghGC.PUNUSED
                                #sghGC.pinUse[5] = sghGC.PUNUSED
                                sghGC.setPinMode()
                                anyAddOns = True

                    if self.bFindOnOff("sghdebug"):
                        if (self.OnOrOff == True) and (debugLogging == False):
                            logging.getLogger().setLevel(logging.DEBUG)
                            debugLogging = True
                        if (self.OnOrOff == False) and (debugLogging == True):
                            logging.getLogger().setLevel(logging.INFO)
                            debugLogging = False

                    if (debugLogging == False):
                        logging.getLogger().setLevel(logging.INFO)

                    if self.bFindOnOff("eventdetect"):
                        sghGC.pinEventEnabled = self.OnOrOff
                        print("pinEvent Detect: ", sghGC.pinEventEnabled)

                    if self.bFindValue("bright"):
                        sghGC.ledDim = int(self.valueNumeric) if self.valueIsNumeric else 100
                        PiGlow_Brightness = sghGC.ledDim
                        print(sghGC.ledDim)

                    if self.bFindValue("triggerreset"):
                        print("triggerreset detected")
                        #print len(self.value) , ("["+self.value+"]")
                        if self.value == "":
                            print("reset all triggers")
                            sghGC.anyTrigger = 0
                            for pin in sghGC.validPins:
                                sghGC.pinTrigger[pin] = 0
                                #print "delaying 5 secs"
                                #time.sleep(5)
                        else:
                            for pin in sghGC.validPins:
                                if sghGC.pinTriggerName[pin] == self.value:
                                    print("trigger reset found", self.value)
                                    sghGC.pinTrigger[pin] = 0
                                    sghGC.anyTrigger = 0




                    if self.bFind("alloff "):
                        with lock:
                            CodeBug.clear()
                            for leg in range(4):
                                CodeBug.setLegInput(leg)

                    if self.bFind("reset "):
                        with lock:
                            CodeBug.clear()
                            for leg in range(4):
                                CodeBug.setLegInput(leg)#


                    for leg in range(4):
                        if self.bFindOnOff("leg"+str(leg)):
                            with lock:
                                CodeBug.output(leg,self.OnOrOff)


                    if self.bFind("clear"):
                        with lock:
                            CodeBug.clear()

                    for pixel in range(25):
                        py = int(pixel / 5)
                        px = pixel % 5
                        #print "pixel" + str(px) + "," + str(py)

                        if self.bFindOnOff("pixel" + str(px) + "," + str(py)):
                            print("match","pixel" + str(px) + "," + str(py))
                            with lock:
                                CodeBug.setPixel(px, py ,self.OnOrOff)
                        elif self.bFindOnOff("pixel"+ str(pixel)):
                            #print "match","pixel"+ str(pixel)
                            with lock:
                                CodeBug.setPixel(px, py, self.OnOrOff)
                        if self.bFindValue("get" + str(px) + "," + str(py)):
                            with lock:
                                state = ["off", "on"][CodeBug.getPixel(px, py)]
                            sensor_name = 'pixelvalue'
                            bcast_str = 'sensor-update "%s" "''%s''"' % (sensor_name, state)
                            msgQueue.put((0,bcast_str))
                        elif self.bFindValue("get"+ str(pixel)):
                            with lock:
                                state = ["off", "on"][CodeBug.getPixel(px, py)]
                            sensor_name = 'pixelvalue'
                            bcast_str = 'sensor-update "%s" "''%s''"' % (sensor_name, state)
                            msgQueue.put((0,bcast_str))

                    for rowcol in range(5):
                        if self.bFindValue("getrow" + str(rowcol)):
                            with lock:
                                value = CodeBug.getRow(rowcol)
                            sensor_name = 'rowvalue'
                            bcast_str = 'sensor-update "%s" "''%s''"' % (sensor_name, value)
                            msgQueue.put((0,bcast_str))
                        elif self.bFindOnOff("row" + str(rowcol)):
                            with lock:
                                CodeBug.setRow(rowcol,31)
                        elif self.bFindValue("row" + str(rowcol) + ","):
                            if self.value[0:2] == "0b":
                                with lock:
                                    CodeBug.setRow(rowcol,int(self.value[2:],2))
                            elif self.valueIsNumeric:
                                with lock:
                                    CodeBug.setRow(rowcol,int(self.value))

                        if self.bFindValue("getcol" + str(rowcol)):
                            with lock:
                                value = CodeBug.getCol(rowcol)
                            sensor_name = 'colvalue'
                            bcast_str = 'sensor-update "%s" "''%s''"' % (sensor_name, value)
                            msgQueue.put((0,bcast_str))
                        elif self.bFindOnOff("col" + str(rowcol)):
                            with lock:
                                CodeBug.setCol(rowcol,31)
                        elif self.bFindValue("col" + str(rowcol) + ","):
                            if self.value[0:2] == "0b":
                                with lock:
                                    CodeBug.setCol(rowcol,int(self.value[2:],2))
                            elif self.valueIsNumeric:
                                with lock:
                                    CodeBug.setCol(rowcol,int(self.value))


                    if self.bFindValue("write"):
                        print("write", self.value)
                        print("caps",datawithCAPS)
                        textpos = datawithCAPS.find('"write')
                        text = datawithCAPS[textpos:]
                        print("text:",text)
                        self.value = text[6:-1]
                        #with lock:
                        #    CodeBug.clear()
                        for i in range(len(self.value) * 5 + 5):
                            with lock:
                                CodeBug.writeText(5 - i, 0,self.value)
                            time.sleep(CodeBug.writeTextDelay)

                    if self.bFindValue("scroll"):
                        if self.value == "left":
                            for row in range(5):
                                old = None
                                with lock:
                                    old = CodeBug.getRow(row)
                                with lock:
                                    CodeBug.setRow(row,(30 & (old * 2)))
                        if self.value == "right":
                            for row in range(5):
                                old = None
                                with lock:
                                    old = CodeBug.getRow(row)
                                with lock:
                                    CodeBug.setRow(row,int(old / 2))

                        if self.value == "up":
                            for row in range(3,-1,-1):
                                old = None
                                with lock:
                                    old = CodeBug.getRow(row)
                                with lock:
                                    CodeBug.setRow(row + 1,old)
                            with lock:
                                CodeBug.setRow(0,0)

                        if self.value == "down":
                            for row in range(0,4):
                                old = None
                                with lock:
                                    old = CodeBug.getRow(row + 1)
                                with lock:
                                    CodeBug.setRow(row,old)
                            with lock:
                                CodeBug.setRow(4,0)




                    #end of normal pin checking

                    if self.bFindValue('pinpattern'):
                        if "pitt" in ADDON:
                            sensor_value = self.value
                            bit_pattern = ('00000000' + self.value)[-8:]
                            print('bit_pattern %s' % bit_pattern)
                            j = 0
                            for pin in [8, 10, 12, 16, 18, 22, 24, 26]:
                                #print "pin" , bit_pattern[-(j+1)]
                                if bit_pattern[-(j + 1)] == '0':
                                    sghGC.pinUpdate(pin, 1)  # output inverted as board is active low
                                else:
                                    sghGC.pinUpdate(pin, 0)
                                j += 1
                        else:
                            #print 'Found pinpattern broadcast'
                            #print dataraw
                            #num_of_bits = PINS
                            outputall_pos = self.dataraw.find('pinpattern')
                            sensor_value = self.dataraw[(outputall_pos + 10):].split()
                            #print sensor_value
                            #sensor_value[0] = sensor_value[0][:-1]
                            #print sensor_value[0]
                            bit_pattern = ('00000000000000000000000000' + sensor_value[0])[-sghGC.numOfPins:]
                            #print 'bit_pattern %s' % bit_pattern
                            j = 0
                            for pin in sghGC.validPins:
                                if (sghGC.pinUse[pin] == sghGC.POUTPUT):
                                    #print "pin" , bit_pattern[-(j+1)]
                                    if bit_pattern[-(j + 1)] == '0':
                                        sghGC.pinUpdate(pin, 0)
                                    else:
                                        sghGC.pinUpdate(pin, 1)
                                    j += 1




                    if self.bFind('gettime'):
                        now = dt.datetime.now()

                        TimeAndDate = now.strftime('%d/%m/%Y %H:%M:%S')
                        #print "tandD" , TimeAndDate
                        sensor_name = 'dateandtime'
                        bcast_str = 'sensor-update "%s" "''%s''"' % (sensor_name, TimeAndDate)
                        msgQueue.put((5,bcast_str))

                        bcast_str = 'sensor-update "day" "''%s''"' % (now.strftime('%a').lower())
                        msgQueue.put((5,bcast_str))




                    if self.bFind("getip"):  #find ip address
                        logging.debug("Finding IP")
                        arg = 'ip route list'
                        p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
                        ipdata = p.communicate()
                        split_data = ipdata[0].split()
                        ipaddr = split_data[split_data.index('src') + 1]
                        logging.debug("IP:%s", ipaddr)
                        sensor_name = 'ipaddress'
                        bcast_str = 'sensor-update "%s" %s' % (sensor_name, "ip" + ipaddr)
                        msgQueue.put((5,bcast_str))




                    if self.bFindValue("prefix"):
                        sghGC.linkPrefix = self.value
                        print("prefix set to", sghGC.linkPrefix)

                    if self.bFindValue('autolink'):
                        try:
                            self.scratch_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.scratch_socket2.connect((self.value, 42001))
                            print(self.scratch_socket2)
                            print("Connected to ", self.value)
                            sghGC.autoLink = True
                            if sghGC.linkPrefix is None:
                                sghGC.linkPrefix = "other"
                        except:
                            print("Failed to connect to ", self.value)
                            pass

                    if self.bFindValue('link'):
                        try:
                            self.scratch_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            self.scratch_socket2.connect((self.value, 42001))
                            print(self.scratch_socket2)
                            print("Connected to ", self.value)
                        except:
                            print("Failed to connect to ", self.value)
                            pass



                    if self.bFindValue('send'):
                        if self.scratch_socket2 is not None:
                            print(self.dataraw)
                            print(self.dataraw.count('send'))
                            #print [match.start() for match in re.finditer(re.escape('send'), self.dataraw)]
                            totalcmd = ''
                            for qwe in self.dataraw.split(" "):
                                #print qwe[0:4]
                                if qwe[0:4] == 'send':
                                    #print qwe
                                    #cmd = qwe[4:]
                                    cmd = 'broadcast "' + qwe[4:] + '"'
                                    #print "sneding:",cmd
                                    n = len(cmd)
                                    b = (chr((n >> 24) & 0xFF)) + (chr((n >> 16) & 0xFF)) + (chr((n >> 8) & 0xFF)) + (
                                        chr(n & 0xFF))
                                    totalcmd = totalcmd + b + cmd
                            #print "Sending to Alt:",totalcmd
                            self.scratch_socket2.send(totalcmd)

                    if self.bFindValue('connect'):
                        cycle_trace = 'disconnected'
                        host = self.value
                        print("cycle_trace has changed to", cycle_trace)
                        break

                    if "version" in dataraw:
                        bcast_str = 'sensor-update "%s" %s' % ("Version", Version)
                        #print 'sending: %s' % bcast_str
                        msgQueue.put((5,bcast_str))


                    if self.bFindValue("getcheerlights"):
                        #print self.value
                        lookupColour = min(10, max(1, int(self.valueNumeric))) if self.valueIsNumeric else 1
                        #print(lookupColour)
                        if (cheerList is None) or (lookupColour == 1):
                            print("Fetching colour from internet")
                            try:
                                cheerList = cheerlights.get_colours()
                            except:
                                print("cheerlight error")
                                cheerList = ['white']
                                pass
                        #print cheerList
                        cheerColour = cheerList[lookupColour - 1]
                        print("new colour", cheerColour)
                        bcast_str = 'sensor-update "%s" %s' % ("cheerlights", cheerColour)
                        msgQueue.put((5,bcast_str))

                        cheerRed = 0
                        cheerGreen = 0
                        cheerBlue = 0
                        if cheerColour in ["red","yellow","white"]:
                            cheerRed = 255

                        if cheerColour in ["purple"]:
                            cheerRed = 128

                        if cheerColour in ["green","yellow","white"]:
                            cheerGreen = 255

                        bcast_str = 'sensor-update "%s" %s' % ("cheerred", cheerRed)
                        msgQueue.put((5,bcast_str))
                        bcast_str = 'sensor-update "%s" %s' % ("cheergreen", cheerGreen)
                        msgQueue.put((5,bcast_str))

                        if self.carryOnInUse == True:
                            bcast_str = 'sensor-update "%s" %s' % ("carryon", "true")
                            msgQueue.put((1,bcast_str))
                        #print "data valid", time.time()

                    #end of broadcast check


                if 'stop handler' in dataraw:
                    print("stop handler msg setn from Scratch")
                    cleanup_threads((listener, sender))
                    sys.exit()

                if self.carryOnInUse == True:
                    bcast_str = 'sensor-update "%s" %s' % ("carryon", "false")
                    msgQueue.put((2,bcast_str))

                self.carryOn = False

        print("Listener Stopped")
                    #else:
                    #print 'received something: %s' % dataraw


###  End of  ScratchListner Class


##Messages to Scratch using a Queue
class SendMsgsToScratch(threading.Thread):
    def __init__(self, socket, msgQueue):
        threading.Thread.__init__(self)
        self.msgQueue = msgQueue
        self.scratch_socket = socket
        self.scratch_socket2 = None
        self._stop = threading.Event()
        print("Send Msgs Init")


    def stop(self):
        self._stop.set()
        print("SendMsgsToScratch Stop Set")

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        print("msgs runnning")
        while not self.stopped():
            #print self.msgQueue.get()
            priority,cmd = self.msgQueue.get()
            if cmd == "STOPSENDING":
                print("STOPSENDING msg retreived from queue")
                self.stop()
                while not self.msgQueue.empty():
                    dummy = self.msgQueue.get()
                break
            # if priority == 1:
            #     print "deque P1 at", time.time()
            n = len(cmd)
            b = (chr((n >> 24) & 0xFF)) + (chr((n >> 16) & 0xFF)) + (chr((n >> 8) & 0xFF)) + (chr(n & 0xFF))
            try:
                self.scratch_socket.send((b + cmd).encode('utf-8'))
            except:
                print("failed to send this message to Scratch", cmd)
                pass
            if self.scratch_socket2 is not None:
                if sghGC.linkPrefix is not None:
                    dataOut = cmd.replace(' "',' "#' + sghGC.linkPrefix + '#')
                else:
                    dataOut = cmd.replace(' "',' "#' + 'other' + '#')
                n = len(dataOut)
                b = (chr((n >> 24) & 0xFF)) + (chr((n >> 16) & 0xFF)) + (chr((n >> 8) & 0xFF)) + (
                    chr(n & 0xFF))
                if sghGC.autoLink:
                    try:
                        self.scratch_socket2.send((b + dataout).encode('utf-8'))
                        print("auto sensor update Sent", dataOut)
                    except:
                        print("failed to send this message to other computer", dataOut)
                        pass

            #print "message sent:" ,cmd

        print("SendMsgsToScratch stopped")


def create_socket(host, port):
    while True:
        try:
            print('Trying')
            scratch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            scratch_sock.connect((host, port))
            break
        except socket.error:
            print("There was an error connecting to Scratch!")
            print("I couldn't find a Mesh session at host: %s, port: %s" % (host, port))
            time.sleep(3)
            #sys.exit(1)

    return scratch_sock


def cleanup_threads(threads):
    print("CLEANUP IN PROGRESS")
    print("Threads told to stop")
    for thread in threads:
        thread.stop()
    print("STOPSENDING msg put in queue")
    msgQueue.put((10,"STOPSENDING"))

    print("Waiting for join on main threads to complete")
    for thread in threads:
        thread.join()


    print("All main threads stopped")

    for pin in sghGC.validPins:
        try:
            print("Stopping ", pin)
            sghGC.pinRef[pin].stop()
            sghGC.pinRef[pin] = None
            sghGC.pinUse[pin] = sghGC.PUNUSED
            sghGC.pinUpdate(pin, 0)
            print("Stopped ", pin)
        except:
            pass

        try:
            if sghGC.pinUse[pin] == sghGC.PSONAR:
                print("Attempting sonar stop on pin:", pin)
                sghGC.pinUltraRef[pin].stop()
                sghGC.pinUse[pin] == sghGC.PUNUSED
                print("Sonar stopped on pin:", pin)
        except:
            pass

        #print "pin use", sghGC.pinUse[pin]
        if sghGC.pinUse[pin] in [sghGC.POUTPUT]:
            sghGC.pinUpdate(pin, 0)
            #print "pin:" ,pin , " set to 0"

    try:
        print("Stopping Matrix")
        PiMatrix.stop()
        print("Stopped ")
    except:
        pass

    print ("cleanup threads finished")


######### Main Program Here


#Set some constants and initialise lists

sghGC = CodeBugController.CodeBugController()
CodeBug = sghGC


ADDON = ""
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)  # default DEBUG - quiwr = INFO

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

PORT = 42001
DEFAULT_HOST = '127.0.0.1'
BUFFER_SIZE = 8192  #used to be 100
SOCKET_TIMEOUT = 2
firstRun = True
lock = threading.Lock()
cheerlights = None



if __name__ == '__main__':
    #SCRIPTPATH = os.path.split(os.path.realpath(__file__))[0]
    #print "PATH:", SCRIPTPATH
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = DEFAULT_HOST
    host = host.replace("'", "")

    GPIOPlus = True
    if len(sys.argv) > 2:
        if sys.argv[2] == "standard":
            GPIOPlus = False

cycle_trace = 'start'
msgQueue = queue.PriorityQueue()


#sghGC.setPinMode()

while True:

    if (cycle_trace == 'disconnected'):
        print("Scratch disconnected")
        cleanup_threads(( listener, sender))
        print("Thread cleanup done after disconnect")
        INVERT = False
        sghGC.resetPinMode()
        print ("Pin Reset Done")
        print()
        print("-------------------------------------------------------------------------------")
        print()
        print()
        print()
        time.sleep(1)
        cycle_trace = 'start'

    if (cycle_trace == 'start'):
        ADDON = ""
        INVERT = False
        # open the socket
        print('Starting to connect...')
        the_socket = create_socket(host, PORT)
        print('Connected!')
        the_socket.settimeout(SOCKET_TIMEOUT)  #removed 3dec13 to see what happens
        listener = ScratchListener(the_socket)



        ##        data = the_socket.recv(BUFFER_SIZE)
        ##        print "Discard 1st data buffer" , data[4:].lower()
        sender = ScratchSender(the_socket)
        sendMsgs = SendMsgsToScratch(the_socket, msgQueue)
        cycle_trace = 'running'
        print("Running....")
        listener.start()
        sender.start()
        sendMsgs.start()

    ##        stepperb.start()


    # wait for ctrl+c
    try:
        #        val = values.pop(0)
        #        values.append(val)
        #        # update the piglow with current values
        #        piglow.update_pwm_values(values)

        time.sleep(0.1)
    except KeyboardInterrupt:
        print ("Keyboard Interrupt")
        cleanup_threads((listener, sender ))
        print("Thread cleanup done after disconnect")
        #time.sleep(5)
        #sghGC.INVERT = False
        sghGC.resetPinMode()
        print ("Pin Reset Done")

        sys.exit()
        print("CleanUp complete")

#### End of main program

