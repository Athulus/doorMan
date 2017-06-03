import urequests
from machine import Pin
import machine
from umqtt.simple import MQTTClient
import time

flag4 = None
flag5 = None
flag6 = None
lockFlag = False
pubFlag = False
motorDone = False
p4 = Pin(4, Pin.IN, Pin.PULL_UP)
p5 = Pin(5, Pin.IN, Pin.PULL_UP)
p1A = Pin(12, Pin.OUT)
p2A = Pin(13, Pin.OUT)
pEN = Pin(14, Pin.OUT)
c = None
pubFeed = None

def setP4Flag(p):
    global flag4
    global flag5
    global flag6
    global lockFlag
    global pubFlag
    global motorDone
    if p.value() == 0:
        flag4 = 1
        if flag5 == 1:
            if flag6 == 1:
                print('door unlocking manually')
                lockFlag = False
                flag4 = 0
                flag5 = 0
                flag6 = 0
                pubFlag = True
                motorDone = True
            else:
                flag6 = 1
                flag5 = 0

def setP5Flag(p):
    global flag4
    global flag5
    global flag6
    global lockFlag
    global pubFlag
    global motorDone
    if p.value() == 0:
        flag5 = 1
        if flag4 == 1:
            if flag6 == 1:
                print('door locking manually')
                lockFlag = True
                flag4 = 0
                flag5 = 0
                flag6 = 0
                pubFlag = True
                motorDone = True
            else:
                flag6 = 1
                flag4 = 0

def pubStatus(c):
    global pubFlag
    global pubFeed
    if lockFlag:
        print('publish locked')
        c.publish(pubFeed,b'0')
    if not lockFlag:
        print('publish unlocked')
        c.publish(pubFeed,b'1')
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
    global p1A
    global p2A
    global pEN
    print('locking')
    #start the motor for lock
    motorForward(p1A,p2A,pEN)
    while not motorDone:
        pass
        # do nothing here, just waiting for intterupt
    #stop motor
    motorStop(p1A,p2A,pEN)
    motorDone = False
    lockFlag = True

def unlock():
    global lockFlag
    global motorDone
    global p1A
    global p2A
    global pEN
    print('unlocking')
    #start the motor for unlock
    motorBackward(p1A,p2A,pEN)
    while not motorDone:
        pass
        # do nothing here, just waiting for intterupt
    #stop motor
    motorStop(p1A,p2A,pEN)
    motorDone = False
    lockFlag = False

def motorForward(p1,p2, pEN):
    pEN.value(0)
    p1.value(1)
    p2.value(0)
    pEN.value(1)

def motorBackward(p1,p2, pEN):
    pEN.value(0)
    p1.value(0)
    p2.value(1)
    pEN.value(1)

def motorStop(p1,p2, pEN):
    pEN.value(0)
    p1.value(0)
    p2.value(0)

def init(myMqttClient, feedURL, username, key, feed):
    global c
    global p5, p4
    global pubFeed
    pubFeed = feed
    print('motor test')
    motorForward(p1A,p2A,pEN)
    time.sleep(0.5)
    motorBackward(p1A,p2A,pEN)
    time.sleep(0.5)
    motorStop(p1A,p2A,pEN)
    print('end motor test')

    c = MQTTClient(myMqttClient, feedURL, 0, username, key)
    c.set_callback(lockStatus_cb)
    c.connect()
    c.subscribe(feed)

    p5.irq(handler=setP5Flag, trigger=Pin.IRQ_FALLING)
    p4.irq(handler=setP4Flag, trigger=Pin.IRQ_FALLING)

def run():
    global c
    global pubFlag
    while(42):
        c.check_msg()
        if pubFlag:
            pubStatus(c)
