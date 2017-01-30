import urequests
from machine import Pin
import machine
from umqtt.simple import MQTTClient

flag4 = None
flag5 = None
lockFlag = False
pubFlag = False
motorDone = False

def setP4Flag(p):
    global flag4
    global flag5
    global lockFlag
    global pubFlag
    global motorDone
    if p.value() == 0:
        flag4 = 1
        if flag5 == 1:
            print('door unlocking manually')
            lockFlag = False
            flag4 = 0
            flag5 = 0
            pubFlag = True
            motorDone = True

def setP5Flag(p):
    global flag4
    global flag5
    global lockFlag
    global pubFlag
    global motorDone
    if p.value() == 0:
        flag5 = 1
        if flag4 == 1:
            print('door locking manually')
            lockFlag = True
            flag4 = 0
            flag5 = 0
            pubFlag = True
            motorDone = True

def pubStatus(c):
    global pubFlag
    if lockFlag:
        print('publish locked')
        c.publish(feed,b'0')
    if not lockFlag:
        print('publish unlocked')
        c.publish(feed,b'1')
    pubFlag = False

def lockStatus_cb(topic, msg):
    global lockFlag
    print(msg)
    if lockFlag and msg ==b'1':
        unlock()
    if not lockFlag and msg ==b'0':
        lock()

def lock():
    global lockFlag
    global motorDone
    print('locking')
    #start the motor for lock
    while not motorDone:
        motorDone = True # this is dumb until i have a motor to control
        # do nothing here, just waiting for intterupt
    #stop motor
    motorDone = False
    lockFlag = True

def unlock():
    global lockFlag
    global motorDone
    print('unlocking')
    #start the motor for unlock
    while not motorDone:
        motorDone = True # this is dumb until i have a motor to control
        # do nothing here, just waiting for intterupt
    #stop motor
    motorDone = False
    lockFlag = False

# url = 'https://a8gp4504z3nci.iot.us-east-1.amazonaws.com/things/doorLock/shadow'
# headers  = {"Authorization:"}
# response = urequests.get(url)
#
# print(response.text)
p4 = Pin(4, Pin.IN, Pin.PULL_UP)
p5 = Pin(5, Pin.IN, Pin.PULL_UP)
print('4: ' + str(p4.value()))
print('5: ' + str(p5.value()))

#
# connect ESP8266 to Adafruit IO using MQTT
#
myMqttClient = "lock-mqtt-client"  # can be anything unique
adafruitIoUrl = "io.adafruit.com"
adafruitUsername = "athulus"  # can be found at "My Account" at adafruit.com
adafruitAioKey = "7f7206bab2a145429298cdd4cc2b6cc4"  # can be found by clicking on "VIEW AIO KEYS" when viewing an Adafruit IO Feed
feed ='athulus/f/doorStatus'
c = MQTTClient(myMqttClient, adafruitIoUrl, 0, adafruitUsername, adafruitAioKey)
c.set_callback(lockStatus_cb)
c.connect()
c.subscribe(feed)

p5.irq(handler=setP5Flag, trigger=Pin.IRQ_FALLING)
p4.irq(handler=setP4Flag, trigger=Pin.IRQ_FALLING)

while(42):
    c.check_msg()
    if pubFlag:
        pubStatus(c)
