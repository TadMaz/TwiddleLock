import spidev
import pigpio 
import time
import Adafruit_MCP3008
import Adafruit_GPIO.SPI as SPI
import threading
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
POT_CHANNEL = 0
BUFFER_MAX = 16
SAMPLING_PERIOD = 0.1

LOCK_MODE = 0
TIMER = time.time()

pi =  pigpio.pi()
SPI_PORT = 0
SPI_DEVICE = 0
MCP = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
values = []
times = []

# Call back global variables
switch_cb, start_cb = 0, 0

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
    STATE_CHANGED = False
    values.insert(0, ADCPOT(MCP.read_adc(POT_CHANNEL)))
    sleep(SAMPLING_PERIOD)
    while True:
        values.insert(0, ADCPOT(MCP.read_adc(POT_CHANNEL)))
        updateValues()
        #print("BUFFER: ",values)
        sleep(SAMPLING_PERIOD)
        if( values[0]-values[1]>0.05 ):
            print("R")
            timethread = Durations(name = "Durations thread!")
            timethread.start()
        elif( abs(values[0]-values[1] )<0.05):
            print("constant")
        elif ( values[0]-values[1]<0.05 ):
            print("L")

def switch_lock_mode(gpio, level, tick):
    global LOCK_MODE
    sleep(0.5) # Debounce time of 0.5 seconds
    if LOCK_MODE == 0:
        LOCK_MODE = 1 # Change to unsecure mode
        print("Selected the unsecure mode")
    else:
        LOCK_MODE = 0 # Change to secure mode
        print("Selected the secure mode")

def main():
    global switch_cb, start_cb
    switch_cb = pi.callback(MODE_SWITCH, pigpio.FALLING_EDGE, switch_lock_mode) # Switch the mode
    start_cb = pi.callback(START_SWITCH, pigpio.FALLING_EDGE, start) # Start the selected mode
    secure_mode()

def start(gpio, level, pin):
    pass

def lock():
    pass


def unlock():
    pass


def sleep(secs):
    tic = time.monotonic()
    while (time.monotonic()-tic < secs):
        pass
#SECURE MODE


def updateValues():
    if len(values)>BUFFER_MAX:
        del values[16]


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

class Durations(threading.Thread):
    def run(self):
        STATE_CHANGED = False
        print("{} started!".format(self.getName()))
        while(not STATE_CHANGED):              
            sleep(SAMPLING_PERIOD)
            if(abs(values[0]-values[1] )<0.05 or values[0]-values[1]<0.05 ):
                times.insert(0,time.monotonic() - TICK)
                print("Durations are :",times)
                STATE_CHANGED = True                                   
        
        print("{} finished!".format(self.getName()))   
if __name__ == "__main__":
    setup()
    main()
