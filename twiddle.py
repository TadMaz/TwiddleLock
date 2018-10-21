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
POT_CHANNEL = 1
BUFFER_MAX = 16
SAMPLING_PERIOD = 0.1

pi =  pigpio.pi()
SPI_PORT = 0
SPI_DEVICE = 0
MCP = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
values = []

def setup():
    
    # Set up the switch pins
    pi.set_mode(START_SWITCH, pigpio.INPUT)
    pi.set_mode(MODE_SWITCH, pigpio.INPUT)
    pi.set_pull_up_down(START_SWITCH, pigpio.PUD_DOWN)
    pi.set_pull_up_down(MODE_SWITCH, pigpio.PUD_DOWN)

def stop():
    READ = False

def ADCPOT(digicode):
    vref = 3.3
    levels = 1024
    vin = (vref*digicode)/ (levels-1)
    return vin

def reset():
    TIMER = time.time()


def secure_mode():

    #read ADC,convert voltages and store values in log
    while True:
        values.insert(1, ADCPOT(MCP.read_adc(POT_CHANNEL)))
        print("Buffer :",values)
        updateValues()
        time.sleep(SAMPLING_PERIOD)
        if( values[0]-values[1]>0 ):
            print("R")
        else:
            print("L")


def updateValues():
    if len(values)>BUFFER_MAX:
        del values[16]

def main():

    ##pi.callback(START_SWITCH, pigpio.FALLING_EDGE,##)
    ##pi.callback(MODE_SWITCH, pigpio.FALLING_EDGE, dothings)
    print(ADCPOT(512))