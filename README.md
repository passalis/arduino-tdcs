# arduino-tdcs
Transcranial Direct Current Stimulation using arduino

**WARNING: Using the code supplied in this project in an inappropriate way may result in SERIOUS INJURIES OR DEATH!**

**The code is provided in the hope that it will be useful for *neuroscientists, doctors, e.t.c.,* but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Before using the code be sure that you understand that [tDCS is dangerous](https://www.eurekalert.org/pub_releases/2016-07/bidm-nwa070816.php) and *experts advise strongly against using it* without proper training.**

## Introduction
[Transcranial Direct Current Stimulation](https://en.wikipedia.org/wiki/Transcranial_direct-current_stimulation) is a neurostimulation technique used by neuroscientists to stimulate specific parts of the brain using electrodes placed on the scalp. A small amount of current, i.e., < 2mA, flows from the electrodes throught the brain. Limited evidence suggests that this technique might be usefull for treating various psychiatric disorders, such as depression.

The purpose of this project is to provide the software needed to perform tDCS using an arduino board, a digital potentiometer and some extra hardware. The arduino is controlled through a PC allowing to set a specific target current and monitoring the device. Then, the arduino constantly adjusts the potentiometer to keep the current within the specfic limit. 

**This is weekend project (build in less than 24 hours) and it has not been thoroughly tested. It is provided with the hope that it will be use useful for any other scientist interested in building and testing a cheap tDCS device. The parts costs (not including the arduino) is less than 5$.**

## Structure

The *arduino* folder  contains the code used in the arduino board (an arduino diecimila was used). The *python* folder  contains a) the code used for talking to arduino using its serial port  and b) the GUI that is used to control the arduino. 

The program runs by executing the gui.py and it was tested under Linux. Ensure that the program have read/write permissions to the serial port.

## Capabilities
The program is capable of:

1. Monitoring the current flowing throught the electrodes and the skin resistance
2. Setting a target current and constantly adjusting the potentiometer to keep it within the target
3. Soft-starting and soft-stoping the tDCS procedure to reduce phosphenes and irritations
4. Protecting from short-circuits

## Hardware

The following hardware is used:

1. Arduino Diecimila
2. 10k Digital Potentiometer (MCP4151)
3. 3 status leds and current-limiting resistor

The arduino uses the SPI serial protocol to talk to the potentiometer and set the appropriate value. The datasheet of the MCP4151 is available [here](http://ww1.microchip.com/downloads/en/DeviceDoc/22060a.pdf). Then the voltage drop over the potentiometer is measured to calculate the current flow as well as the output resistance. The pinout is defined in the arduino code and it should straightforward to construct the device if you have basic electronic skills.  The one electrode is connected to the ground, while the other one is driven using 5 volt from the USB port and the MCP4151.

## Photos

Some photos of the device is provided bellow, as well as some measurements to show the capability of the device of setting an maintaining a target current flow (within the limits of the hardware design: the wiper resistance is 75 Ohms and the minimum short-circuit current is 0.5mA).
