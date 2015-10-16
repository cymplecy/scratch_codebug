### ALPHA CODE/INSTRUCTIONS _ PLEASE TEST BUT EXPECT ERRORS :)
####I2C tethering for Codebug on RaspberryPi

This allows you to control the Codebug from Scratch on the RaspberryPi by plugging it into the Pins

**Setting Up**
Follow all instructions about getting it working in Python from the [main codebug website](http://codebug-i2c-tether.readthedocs.org/en/latest/) and make sure it works


Then download the ScratchCodebug respositry (https://github.com/cymplecy/scratch_codebug) from Github as a zip file into /home/pi

type

    unzip scratch_codebug_master.zip


**Using ScratchCodeBug**
Launch LX Terminal and type

    cd scratch_codebug_master.zip
    
    sudo python3 ScratchCodeBug.py

this will start the handler

Switch to desktop and run Scratch.

Select sensors block and right-click on bottom sensor block and enable Remote Sensor Connections

You should be up and running - goto http://simplesi.net/scratchcodebug-beta-testing/ for ScratchCodeBug syntax


