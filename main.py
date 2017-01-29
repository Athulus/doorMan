import urequests
from machine import Pin
import machine
from umqtt.simple import MQTTClient

flag4 = None
flag5 = None
lockFlag = False
unlockFlag = None

def readPin(inputPin):
    return inputPin.value()

def setP4Flag(p):
    global flag4
    global flag5
    global unlockFlag
    if p.value() == 0:
        flag4 = 1
        if flag5 == 1:
            print('door unlocking')
            unlockFlag = True
            flag4 = 0
            flag5 = 0

def setP5Flag(p):
    global flag4
    global flag5
    global lockFlag
    if p.value() == 0:
        flag5 = 1
        if flag4 == 1:
            print('door locking')
            lockFlag = True
            flag4 = 0
            flag5 = 0

def markLock(c):
    print("lock status sent")
    c.publish('Locked')
    lockFlag = False

def markUnlock(c):
    print("unlock status sent")
    c.publish('Unlocked')
    unlockFlag = False

def toggleLock():
    if lockFlag:
        print('unlocking')
    if unlockFlag:
        print('locking')

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
myMqttClient = "max-mqtt-client"  # can be anything unique
adafruitIoUrl = "io.adafruit.com"
adafruitUsername = "athulus"  # can be found at "My Account" at adafruit.com
adafruitAioKey = "7f7206bab2a145429298cdd4cc2b6cc4"  # can be found by clicking on "VIEW AIO KEYS" when viewing an Adafruit IO Feed
c = MQTTClient(myMqttClient, adafruitIoUrl, 0, adafruitUsername, adafruitAioKey)
c.set_callback(toggleLock)
c.connect()
c.subscribe('athulus/f/doorStatus')

p5.irq(handler=setP5Flag, trigger=Pin.IRQ_FALLING)
p4.irq(handler=setP4Flag, trigger=Pin.IRQ_FALLING)

while(42):
    c.wait_msg()
    if lockFlag :
        markLock(c)

    if unlockFlag:
        markUnlock(c)
