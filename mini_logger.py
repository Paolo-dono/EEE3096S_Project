import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import threading
import time
from datetime import datetime
import RPi.GPIO as GPIO
import ES2EEPROMUtils
import os

spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI) #spi bus
cs = digitalio.DigitalInOut(board.D5) #chip select
mcp = MCP.MCP3008(spi, cs)
chan = AnalogIn(mcp, MCP.P0)
button = 16
buzzer_pin = 24
start_run = False
eeprom = ES2EEPROMUtils.ES2EEPROM()
start_time = ""

def setup():
    global buzzer
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(button, GPIO.RISING, callback=start, bouncetime=200)
    GPIO.setup(buzzer_pin, GPIO.OUT)

def sensor_vals():
    global buzzer_pin
    global start_run
    global start_time
    
    count = 0
    while start_run:
        curr_time = datetime.now()
        sys_time = str(curr_time-start_time).split(".")[0]
        if sys_time.index(":") == 1:
            sys_time = "0" + sys_time
        curr_time = curr_time.strftime("%H:%M:%S")
        temp = round((chan.voltage-0.5)*100)
        
        if count%5 == 0:
            print(curr_time + '\t' + sys_time + '\t', temp, 'C\t*')
            buzz()
            time.sleep(4.9)
        else:
            print(curr_time + '\t' + sys_time + '\t', temp, 'C')
            time.sleep(5)
        count+=1
        
        store(curr_time, temp)

def read_log():
    global eeprom
    
    raw_data = eeprom.read_block(0, 180)
    data = []
    for i in range(0, 20):
        curr_time = ""
        for j in range(0, 8):
            curr_time = curr_time + chr(raw_data[(i*9)+j])
        data.append([curr_time, raw_data[(i+1)*9-1]])
    return data
    
def store(new_time, new_temp):
    global eeprom
    
    raw_data = eeprom.read_block(0, 171)
    raw_time = ""
    for i in range(0, 8):
        raw_data.insert(i, ord(new_time[i]))
    raw_data.insert(8, new_temp)
    eeprom.write_block(0, raw_data)

def buzz():
    global buzzer_pin
    
    GPIO.output(buzzer_pin, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(buzzer_pin, GPIO.LOW)

def start(channel):
    global start_run
    
    if start_run == False:
        start_run = True
        os.system("clear")
        print("Logging has started (Press the button to stop logging)")
        print("Time\t\tSys Timer\t Temp\tBuzzer")
        x = threading.Thread(target=sensor_vals)
        x.start()
    else:
        start_run = False
        os.system("clear")
        print("Logging has stopped (Press the button to start logging)")

if __name__ == "__main__":
    try:
        start_time = datetime.now()
        os.system("clear")
        print("Welcome to the Terrarium Logger! Press the button to start logging.")
        setup()
        while True:
            time.sleep(5)
    except Exception as e:
        print(e)
    except KeyboardInterrupt as k:
        print("Exiting")
    finally:
        GPIO.cleanup()
        
    
