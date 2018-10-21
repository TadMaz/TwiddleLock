import spidev
import SPI
import pigpio 
import time
import Adafruit_MCP3008

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
FREQ = 100 # Frequency of reading MCP
READ = True

LOCK_MODE = 0
TIMER = time.time()

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

def switch_lock_mode(gpio, level, tick):
    global LOCK_MODE
    sleep(0.5) # Debounce time of 0.5 seconds
    if LOCK_MODE == 0:
        LOCK_MODE = 1
        print("Selected the unsecure mode")
    else:
        LOCK_MODE = 0
        print("Selected the secure mode")

def main():

    pi.callback(MODE_SWITCH, pigpio.FALLING_EDGE, switch_lock_mode) # Switch the mode
    pi.callback(START_SWITCH, pigpio.FALLING_EDGE) # Start the selected mode

def lock():
    pass


def unlock():
    pass


def sleep(secs):
    tic = time.monotonic()
    while (time.monotonic()-tic < secs):
        pass
#SECURE MODE



#UNSECURE MODE

DURATIONS = []
TICK = 0
TOCK = 0 
KEY = [1, 1, 2]

def unsecure_mode():
    global pi, TICK, DURATIONS
    print("Starting unsecure mode")
    reading = MCP.read(0) # POT is on channel 0
    while (MCP.read(0) == reading):
        pass
    TICK = time.monotonic()
    print("Now taking readings")
    while(len(DURATIONS)< len(KEY)):
        while (reading != MCP.read(0)):
            reading = MCP.read(0)
            time.sleep(1/FREQ)
        DURATIONS.append(time.monotonic() - TICK)
        while(reading == MCP.read(0)):
            pass
    print("Code entered")
    DURATIONS.sort()
    print("Checking code")
    if (unsecure_check()):
        print("Code correct")
        unlock()
    else:
        print("Code incorrect")
        lock()

def unsecure_check():
    for i in range(len(KEY)):
        if KEY[i] != DURATIONS[i]:
            return False
    return True

if __name__ == "__main__":
    setup()
    main()
