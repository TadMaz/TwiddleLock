import spidev
import pigpio 
import time
import RPi.GPIO as GPIO
import Adafruit_MCP3008
import Adafruit_GPIO.SPI as SPI
import threading
import math
#GPIO Pins

START_SWITCH = 2
MODE_SWITCH = 3

LOCK_LIGHT = 17
UNLOCK_LIGHT = 27
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
durations_list = []
directions_list = []


UNLOCK_KEY = ["1.0", "1.0", "2.0", "2.0"]
SECURE_UNLOCK_KEY = ["L1.0", "R1.0", "L1.0", "R1.0"]
# Call back global variables
switch_cb, start_cb = 0, 0

def setup():
    
    # Set up the switch pins
    GPIO.setup(START_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(MODE_SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LOCK_LIGHT, GPIO.OUT)
    GPIO.setup(UNLOCK_LIGHT, GPIO.OUT)

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
    print("Starting secure mode")
    #start Directions and Duration threads
    direc  = Directions(name = "Directions thread")
    sleep(SAMPLING_PERIOD)
    durat  = Durations(name = "Durartions thread")
    
    direc.start()
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
    lock()
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
    GPIO.output(LOCK_LIGHT, GPIO.HIGH)
    GPIO.output(UNLOCK_LIGHT, GPIO.LOW)
    print("Locked")


def unlock():
    GPIO.output(UNLOCK_LIGHT, GPIO.HIGH)
    GPIO.output(LOCK_LIGHT, GPIO.LOW)
    print("Unlocked")


def sleep(secs):
    tic = time.monotonic()
    while (time.monotonic()-tic < secs):
        pass
#SECURE MODE


def updateBuffer(buffer):
    if len(buffer) > BUFFER_MAX:
        for i in range(len(buffer)-1,BUFFER_MAX-1,-1):
            del buffer[i]

def updateDurations():
    for i in times:
        durations_list.append( round(i) )
    updateBuffer(durations_list)

#UNSECURE MODE

DURATIONS = []
TICK = 0
TOCK = 0 


def unsecure_mode():
    global pi, TICK, DURATIONS
    print("Starting unsecure mode")
    direc  = Directions(name = "Directions thread")
    sleep(SAMPLING_PERIOD)
    durat  = Durations(name = "Durartions thread")
    
    direc.start()
    durat.start()
    
def unsecure_check():
    if len(durations_list) !=  len(UNLOCK_KEY):
        print(durations_list)
        print("Lengths not equal")
        return False
    entered_key = []
    for i in range(len(durations_list)):
        entered_key.append(str(durations_list[i]))
    for i in range(len(durations_list)):
        if entered_key[i] != UNLOCK_KEY[i]:
            return False
    return True



def secure_check():

    # First check for equal length lists
    if len(durations_list) != len(directions_list):
        print(durations_list)
        print(directions_list)
        print("Lengths not equal")
        return False
    if len(SECURE_UNLOCK_KEY) !=  len(durations_list):
        print("Entered length not equal to KEY length")
        return False
    entered_key = []
    for i in range(len(durations_list)):
        entered_key.append(directions_list[i] + str(durations_list[i]))
    entered_key.reverse()
    print(entered_key)
    for i in range(len(entered_key)):
        if entered_key[i] != SECURE_UNLOCK_KEY[i]:
            return False
    return True
    
    # Check for equality

class Durations(threading.Thread):
    def run(self):
        print("{} started!".format(self.getName()))
        while True:
            STATE_CHANGED = False
            reading = round( ADCPOT( MCP.read_adc(0) ), 2 )
            while (len(values)<2 and abs(reading - round(ADCPOT(MCP.read_adc(0)), 2)) < 0.2):
                pass
            TICK = time.monotonic()
            while(not STATE_CHANGED):              
                sleep(SAMPLING_PERIOD)
                if(len(values)>1 and values[0]-values[1] <-0.1 ):          #moving to right
                    while(values[0]-values[1] <-0.1):
                        sleep(0.05)                      #check whether it is still increasing
                        continue
                    times.insert(0,time.monotonic() - TICK)
                    updateBuffer(times)
                    #updateDurations()
                    print("Durations are :",times)
                    STATE_CHANGED = True
                elif(len(values)>1 and values[0]-values[1] >0.1 ):       #moving to left
                    while( values[0]-values[1] >0.1 ):
                        sleep(0.05)                     #check whether it is still increasing
                        continue
                    times.insert(0,time.monotonic() - TICK)
                    updateBuffer(times)
                    #updateDurations()
                    print("Durations are :",times)
                    STATE_CHANGED = True
                elif ( time.monotonic() - TICK> 5 ):
                    exit_by_delay()



class Directions(threading.Thread):
    def run(self):
        print("{} started!".format(self.getName()))
        reading = round(ADCPOT(MCP.read_adc(0)), 2)
        while(len(values)<2 and abs(reading - round(ADCPOT(MCP.read_adc(0)), 2)) < 0.2):
            pass
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
                updateBuffer(directions_list)
                #print("constant")
            elif ( values[0]-values[1]<-0.1 ):                 #when values decrease->right
                while(values[0]-values[1] <-0.1):              #check whether it is still increasing
                    values.insert(0, ADCPOT(MCP.read_adc(POT_CHANNEL)))
                    sleep(SAMPLING_PERIOD)    
                print("R") 
                directions_list.insert(0,"R")
                updateBuffer(directions_list)                         


def exit_by_delay():
    global durations_list
    print("Exiting")
    print(directions_list)
    durations_list = round_all(times)
    durations_list.sort()
    print(durations_list)
    if LOCK_MODE == 0:
        if secure_check():
            unlock()
        else:
            lock()
    else:
        if unsecure_check():
            unlock()
        else:
            lock()
    exit()

def round_to_5(value):
    """
    root = math.floor(value)
    decimal = value - root
    if decimal >= 0.5:
        decimal = 0.5
    else:
        decimal = 0.0
    return round(root + decimal, 1)
    """
    return round(value, 0)

def round_all(alist):
    newlist = []
    for item in alist:
        newlist.append(round_to_5(item))
    return newlist

if __name__ == "__main__":
    setup()
    main()
    GPIO.cleanup()
