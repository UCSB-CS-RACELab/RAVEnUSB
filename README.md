RAVEnUSB
========
This program allows you to read/write a Rainforest RAVEn USB device connected
to a Mac OSX machine.  Program runs with no command line arguments. Change the
logging level to Debug if you want to see the verbose output in raven.log in
the current working directory.  The output of the program is
<br>Device epoch:local epoc:message type:value
<br>

<ol><li>Install the FTDI driver, reboot:
<a
href="http://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf">http://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf</a>
</li><li>Get the USB Product Name for xml key (next step): ioreg -p IOUSB -l -b
</li><li> Edit
/System/Library/Extensions/FTDIUSBSerialDriver.kext/Contents/Info.plist
and add this entry under 
```xml
<key>IOKitPersonalities</key>

<key>RFA-Z106-RA-PC RAVEn v2.3.21</key>
<dict>
      <key>CFBundleIdentifier</key>
      <string>com.FTDI.driver.FTDIUSBSerialDriver</string>
      <key>IOClass</key>
      <string>FTDIUSBSerialDriver</string>
      <key>IOProviderClass</key>
      <string>IOUSBInterface</string>
      <key>bConfigurationValue</key>
      <integer>1</integer>
      <key>bInterfaceNumber</key>
      <integer>0</integer>
      <key>idProduct</key>
      <integer>35368</integer>
      <key>idVendor</key>
      <integer>1027</integer>
</dict>
```
</li><li> reboot, insert USB device
</li><li> verify that you see the device as /dev/cu.usbserial-XXX 
for some XXX
</li><li> verify that you are hearing the device via 
<br>
screen /dev/cu.usbserial-XXX 115200
<br>
This will output: every 8 seconds instantaneous demand, 
every few minutes: ConnectionStatus, 
every few minutes: CurrentSummationDelivered.
<br>
use Ctrl-A Ctrl-] to exit
</li><li>update serialDevice variable in raven.py with the name of device in /dev
</li></ul>

<p/>
<b>Useful references:<b>
<br>
<a
href="http://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf">http://www.ftdichip.com/Support/Documents/InstallGuides/Mac_OS_X_Installation_Guide.pdf</a>
<br><a
href="http://forums.whirlpool.net.au/archive/1928671">http://forums.whirlpool.net.au/archive/1928671</a>
debbiep July 3, 2012 8:02pm + debbiep July 5, 2012, 7:20am


