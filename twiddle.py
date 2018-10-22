import spidev
import pigpio 
import time
import RPi.GPIO as GPIO
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
FREQ = 10 # Frequency of reading MCP
READ = True
POT_CHANNEL = 0
BUFFER_MAX = 16
SAMPLING_PERIOD = 0.2

LOCK_MODE = 0
TIMER = time.time()

GPIO.setmode(GPIO.BCM)
SPI_PORT = 0
SPI_DEVICE = 0
MCP = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
values = []
times = []
durations_list = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
directions_list = []

# Call back global variables
switch_cb, start_cb = 0, 0

def setup():
    
    # Set up the switch pins
    GPIO.setup(START_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(MODE_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

    #start Directions and Duration threads
    direc  = Directions(name = "Directions thread")
    durat  = Durations(name = "Durartions thread")
    
    direc.start()
    sleep(SAMPLING_PERIOD)
    durat.start()

def switch_lock_mode(gpio):
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
    GPIO.add_event_detect(MODE_SWITCH, GPIO.FALLING, callback=switch_lock_mode, bouncetime=1000) # Switch the mode
    GPIO.add_event_detect(START_SWITCH, GPIO.FALLING, callback=start, bouncetime=1000) # Start the selected mode
    while (True):
        pass
    

def start(gpio):
    GPIO.remove_event_detect(START_SWITCH)
    GPIO.remove_event_detect(MODE_SWITCH)
    sleep(1)
    if LOCK_MODE == 0:
        secure_mode()
    else:
        unsecure_mode()

def lock():
    print("Locked")


def unlock():
    print("Unlocked")


def sleep(secs):
    tic = time.monotonic()
    while (time.monotonic()-tic < secs):
        pass
#SECURE MODE


def updateBuffer(buffer):
    if len(buffer) > BUFFER_MAX:
        for i in range(len(buffer),15):
            del buffer[i]

def updateDurations():
    for i in range(len(times)-1):
        durations_list[i] = round(times[i])
    updateBuffer(durations_list)

#UNSECURE MODE

DURATIONS = []
TICK = 0
TOCK = 0 
KEY = [1, 1, 2]

def unsecure_mode():
    global pi, TICK, DURATIONS
    print("Starting unsecure mode")
    reading = round(ADCPOT(MCP.read_adc(0)), 2)  # POT is on channel 0
    print(reading)
    while(abs(reading - round(ADCPOT(MCP.read_adc(0)), 2)) <= 0.2):
        pass
    TICK = time.monotonic()
    print("Now taking readings")
    while(len(DURATIONS)< len(KEY)):
        while(abs(reading - round(ADCPOT(MCP.read_adc(0)), 2)) > 0.2):
            reading = round(ADCPOT(MCP.read_adc(0)), 2)
            time.sleep(1/FREQ)
            print(reading)
        DURATIONS.append(round(time.monotonic() - TICK, 1))
        TICK = time.monotonic()
        while(abs(reading - round(ADCPOT(MCP.read_adc(0)), 2)) <= 0.2):
            pass
    print("Code entered")
    DURATIONS.sort()
    print("Checking code")
    if (unsecure_check()):
        print(DURATIONS)
        print("Code correct")
        unlock()
    else:
        print(DURATIONS)
        print("Code incorrect")
        lock()

def unsecure_check():
    for i in range(len(KEY)):
        if KEY[i] != DURATIONS[i]:
            return False
    return True

class Durations(threading.Thread):
    def run(self):
        print("{} started!".format(self.getName()))
        while True:
            STATE_CHANGED = False
            TICK = time.monotonic()
            while(not STATE_CHANGED):              
                sleep(SAMPLING_PERIOD)
                if(values[0]-values[1] <-0.1 ):          #moving to right
                    while(values[0]-values[1] <-0.1):
                        sleep(0.05)                      #check whether it is still increasing
                        continue
                    times.insert(0,time.monotonic() - TICK)
                    updateBuffer(times)
                    updateDurations()
                    print("Durations are :",durations_list)
                    STATE_CHANGED = True
                elif( values[0]-values[1] >0.1 ):       #moving to left
                    while( values[0]-values[1] >0.1 ):
                        sleep(0.05)                     #check whether it is still increasing
                        continue
                    times.insert(0,time.monotonic() - TICK)
                    updateBuffer(times)
                    updateDurations()
                    print("Durations are :",durations_list)
                    STATE_CHANGED = True
                elif ( time.monotonic() - TICK>2  ):
                    exit_by_delay()



class Directions(threading.Thread):
    def run(self):
        print("{} started!".format(self.getName()))
        values.insert(0, ADCPOT(MCP.read_adc(POT_CHANNEL)))
        sleep(SAMPLING_PERIOD)
        while True:
            values.insert(0, ADCPOT(MCP.read_adc(POT_CHANNEL)))
            updateBuffer(values)
            #print("BUFFER: ",values)
            sleep(SAMPLING_PERIOD)
            if( values[0]-values[1]>0.1 ):                     #when values increase->left
                while(values[0]-values[1] >0.1):              #check whether it is still increasing
                    values.insert(0, ADCPOT(MCP.read_adc(POT_CHANNEL)))
                    sleep(SAMPLING_PERIOD)
                print("L")
                directions_list.insert(0,"L")
                #print("constant")
            elif ( values[0]-values[1]<-0.1 ):                 #when values decrease->right
                while(values[0]-values[1] <-0.1):              #check whether it is still increasing
                    values.insert(0, ADCPOT(MCP.read_adc(POT_CHANNEL)))
                    sleep(SAMPLING_PERIOD)    
                print("R") 
                directions_list.insert(0,"R")                         


def exit_by_delay():
    print("Exiting")
    print(directions_list)
    print(durations_list)
    GPIO.cleanup()
    exit()

if __name__ == "__main__":
    setup()
    main()
    GPIO.cleanup()
