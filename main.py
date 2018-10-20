import RPi.GPIO as GPIO
import spidev
import SPI

import time

# GPIO Switch Pins
RESET_SWITCH = 2
FREQ_SWITCH = 3
STOP_SWITCH = 4
DISPLAY_SWITCH = 17
# GPIO SPI Pins
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8

# Global variables
FREQ = 0
TIMER = 0
READ = True

spi = spidev.SpiDev()
spi.open(0,0)

SPI_PORT = 0
SPI_DEVICE = 0
MCP = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
READINGS = []

def setup():

    #Set the GPIO mode

    GPIO.setmode(GPIO.BCM)
    
    # Set up the switch pins

    GPIO.setup(RESET_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(FREQ_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(STOP_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(DISPLAY_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def switch_frequency():
    if FREQ == 0.5:
        FREQ = 1
    elif FREQ == 1:
        FREQ = 2
    else:
        FREQ = 0.5

def stop():
    READ = False


def display():
    # Display first five readings
    print("_____________________________")
    print("{0:8} {1:8} {2:4} {3:4} {4:5}".format("Time", "Timer", "Pot", "Temp", "Light"))
    print("_____________________________")
    for reading in READINGS:
        reading.printReading()
        print("_____________________________")


class Reading:

    def __init__(self, time, pot, temp, light):
        self.time = time
        self.pot = pot
        self.temp = temp
        self.light = light

    def printReading(self):
        print("{0:8} {1:8} {2:3}V {3:2}C {4:2}%"
              .format(self.gettime(), self.gettimer(), self.getpot(), self.gettemp(), self.getlight()))

    def gettime(self):
        return time.localtime(self.time)

    def gettimer(self):
        return self.time - TIMER

    def getpot(self):
        return ADCPOT(self.pot)

    def getlight(self):
        return self.light

    def gettemp(self):
        return ADCTEMP(self.temp)



def ADCPOT(value):
    max = 3.3
    levels = 1024
    return max/(levels-1) *value

def ADCTEMP(value):
    levels = 1024
    max =3.3
    voltage = max/(levels-1)* value
    return temp

def reset():
    TIMER = time.time()

def main():

    GPIO.add_event_detect(RESET_SWITCH, GPIO.FALLING, callback=reset, bouncetime=200)
    GPIO.add_event_detect(STOP_SWITCH, GPIO.FALLING, callback=stop, bouncetime=200)
    GPIO.add_event_detect(DISPLAY_SWITCH, GPIO.FALLING, callback=display, bouncetime=200)
    GPIO.add_event_detect(FREQ_SWITCH, GPIO.FALLING, callback=switch_frequency, bouncetime=200)
    while(1):
        while (READ):
            READINGS.append(Reading(
                time.time(), MCP.read_adc(0), MCP.read_adc(1), MCP.read_adc(2)
                ))
            time.sleep(1/FREQ)
    GPIO.cleanup()

main()
GPIO.cleanup()
