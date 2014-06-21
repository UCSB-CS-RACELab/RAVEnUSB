#!/usr/bin/python

import sys
import datetime
import serial
import time
import xml.etree.ElementTree as ET
import re
import logging as log

####################
''' adapted from https://github.com/frankp/python-raven '''
''' author: Chandra Krintz '''
####################

'''   Setup Steps
1) Install the FTDI driver, reboot:
http://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf
2) Get the USB Product Name for xml key (next step): ioreg -p IOUSB -l -b
3) Edit
/System/Library/Extensions/FTDIUSBSerialDriver.kext/Contents/Info.plist
and add this entry under <key>IOKitPersonalities</key>
4) reboot, insert USB device
5) verify that you see the device as /dev/cu.usbserial-XXX 
for some XXX
6) verify that you are hearing the device via 
screen /dev/cu.usbserial-XXX 115200
use Ctrl-A Ctrl-] to exit
7) update serialDevice variable below with name of device in /dev
'''
   
serialDevice = "/dev/cu.usbserial-00001004"

####################

# Logging setup
log.basicConfig(filename='raven.log',level=log.ERROR)

# Various Regex's
reStartTag = re.compile('^<[a-zA-Z0-9]+>') # to find a start XML tag (at very beginning of line)
reEndTag = re.compile('^<\/[a-zA-Z0-9]+>') # to find an end XML tag (at very beginning of line)

def sendCommand(serialport, command):
  '''Given a command it will be formatted in XML and written to serialport for RAVEn device'''
  # Sends a simple command, such as initialize, get_instantaneous_demand, etc.
  output = ("<Command>\n  <Name>%s</Name>\n</Command>" % command)
  log.info("Issuing command: " + command)
  serialport.write(output)
  time.sleep(0.5) # allow this command to sink in

def getCurrentSummationKWh(xmltree):
  '''Returns a single float value for the SummationDelivered from a Summation response from RAVEn'''
  # Get the Current Summation (Meter Reading)
  fReading = float(int(xmltree.find('SummationDelivered').text,16))
  fResult = calculateRAVEnNumber(xmltree, fReading)
  return formatRAVEnDigits(xmltree, fResult)

def getInstantDemandKWh(xmltree):
  '''Returns a single float value for the Demand from an Instantaneous Demand response from RAVEn'''
  # Get the Instantaneous Demand
  fDemand = float(int(xmltree.find('Demand').text,16))
  fResult = calculateRAVEnNumber(xmltree, fDemand)
  return formatRAVEnDigits(xmltree, fResult)

def calculateRAVEnNumber(xmltree, value):
  '''Calculates a float value from RAVEn using Multiplier and Divisor in XML response'''
  # Get calculation parameters from XML - Multiplier, Divisor
  fDivisor = float(int(xmltree.find('Divisor').text,16))
  fMultiplier = float(int(xmltree.find('Multiplier').text,16))
  if (fMultiplier > 0 and fDivisor > 0):
    fResult = float( (value * fMultiplier) / fDivisor)
  elif (fMultiplier > 0):
    fResult = float(value * fMultiplier)
  else: # (Divisor > 0) or anything else
    fResult = float(value / fDivisor)
  return fResult

def formatRAVEnDigits(xmltree, value):
  '''Formats a float value according to DigitsRight, DigitsLeft and SuppressLeadingZero settings from RAVEn XML response'''
  # Get formatting parameters from XML - DigitsRight, DigitsLeft
  iDigitsRight = int(xmltree.find('DigitsRight').text,16)
  iDigitsLeft = int(xmltree.find('DigitsLeft').text,16)
  sResult = ("{:0%d.%df}" % (iDigitsLeft+iDigitsRight+1,iDigitsRight)).format(value)
  # Suppress Leading Zeros if specified in XML
  if xmltree.find('SuppressLeadingZero').text == 'Y':
    while sResult[0] == '0':
      sResult = sResult[1:]
  return sResult

def main():
  # open serial port
  ser = serial.Serial(serialDevice, 115200, serial.EIGHTBITS, serial.PARITY_NONE, timeout=0.5)
  
  '''command options:
  http://rainforestautomation.com/sites/default/files/download/rfa-z106/raven_xml_api_r127.pdf
  Send a command then go into the loop and response will be recieved some 
  time thereafter.  Most command outputs are not handled yet herein.
  '''
  #sendCommand(ser, "get_current_summation_delivered")
  #sendCommand(ser, "get_instantaneous_demand")
  #sendCommand(ser, "get_time")
  #sendCommand(ser, "get_schedule")
  #sendCommand(ser, "get_meter_list")
  #sendCommand(ser, "get_network_info")
  #sendCommand(ser, "get_current_price")
  #sendCommand(ser, "get_message")
  #sendCommand(ser, "get_device_info")
  #sendCommand(ser, "get_connection_status")

  rawxml = ''
  try:
    while True:
      ravenline = ser.readline()
      log.debug("Received string from serial: [[" + ravenline + "]]")
      ravenline = ravenline.strip('\0')
      if len(ravenline) > 0:
        # start tag
        if reStartTag.match(ravenline):
          rawxml = ravenline
        # end tag
        elif reEndTag.match(ravenline):
          rawxml = rawxml + ravenline
          val = 0.0
          try:
            xmltree = ET.fromstring(rawxml)
            if xmltree.tag == 'CurrentSummationDelivered':
              val = getCurrentSummationKWh(xmltree)
            elif xmltree.tag == 'InstantaneousDemand':
              val = getInstantDemandKWh(xmltree)
            else:
              log.warning("*** Unimplemented XML Fragment")
              log.warning(rawxml)
          except Exception as e:
            log.error("Exception triggered: " + str(e))
            rawxml = ''
            continue

	  #the date may be unset in the device
          ts = float(int(xmltree.find('TimeStamp').text,16))
          myts = time.time()
          print '{0}:{1}:{2}:{3}'.format(ts,myts,xmltree.tag,val)
        
          rawxml = ''

        # if it starts with a space, it's inside the fragment
        else:
          rawxml = rawxml + ravenline
          log.debug("Normal inner XML Fragment: " + ravenline)
     
      #else: skip the line

  except KeyboardInterrupt: 
    print '\nRAVEn read loop terminated by keyboard interrupt'
    ser.close()

if __name__ == '__main__':
  main()
