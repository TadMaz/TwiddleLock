import spidev
import SPI
import pigpio 
import time

#GPIO Pins

START_SWITCH = 2
MODE_SWITCH = 3

#SPI

# GPIO SPI Pins
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8

# Global variables
FREQ = 0
READ = True

pi =  pigpio.pi()
SPI_PORT = 0
SPI_DEVICE = 0
MCP = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
READINGS = []

def setup():
    
    # Set up the switch pins
    pi.set_mode(START_SWITCH, pigpio.INPUT)
    pi.set_mode(MODE_SWITCH, pigpio.INPUT)
    pi.set_pull_up_down(START_SWITCH, pigpio.PUD_DOWN)
    pi.set_pull_up_down(MODE_SWITCH, pigpio.PUD_DOWN)

def stop():
    READ = False

def ADCPOT(value):
    max = 3.3
    levels = 1024
    return max/(levels-1) *value

def reset():
    TIMER = time.time()

def main():

    pi.callback(START_SWITCH, pigpio.FALLING_EDGE,##)
    pi.callback(MODE_SWITCH, pigpio.FALLING_EDGE, dothings)
      
#SECURE MODE



#UNSECURE MODE