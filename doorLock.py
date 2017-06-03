import time
import urequests
from machine import Pin
import machine
from umqtt.simple import MQTTClient

FLAG4 = None
FLAG5 = None
FLAG6 = None
LOCK_FLAG = False
PUB_FLAG = False
MOTOR_DONE = False
P4 = Pin(4, Pin.IN, Pin.PULL_UP)
P5 = Pin(5, Pin.IN, Pin.PULL_UP)
P1A = Pin(12, Pin.OUT)
P2A = Pin(13, Pin.OUT)
P_EN = Pin(14, Pin.OUT)
C = None
PUB_FEED = None


def setP4Flag(p):
    global FLAG4
    global FLAG5
    global FLAG6
    global LOCK_FLAG
    global PUB_FLAG
    global MOTOR_DONE
    if p.value() == 0:
        FLAG4 = 1
        if FLAG5 == 1:
            if FLAG6 == 1:
                print('door unlocking manually')
                LOCK_FLAG = False
                FLAG4 = 0
                FLAG5 = 0
                FLAG6 = 0
                PUB_FLAG = True
                MOTOR_DONE = True
            else:
                FLAG6 = 1
                FLAG5 = 0


def setP5Flag(p):
    global FLAG4
    global FLAG5
    global FLAG6
    global LOCK_FLAG
    global PUB_FLAG
    global MOTOR_DONE
    if p.value() == 0:
        FLAG5 = 1
        if FLAG4 == 1:
            if FLAG6 == 1:
                print('door locking manually')
                LOCK_FLAG = True
                FLAG4 = 0
                FLAG5 = 0
                FLAG6 = 0
                PUB_FLAG = True
                MOTOR_DONE = True
            else:
                FLAG6 = 1
                FLAG4 = 0


def pubStatus(c):
    global PUB_FLAG
    global PUB_FEED
    if LOCK_FLAG:
        print('publish locked')
        c.publish(PUB_FEED, b'0')
    if not LOCK_FLAG:
        print('publish unlocked')
        c.publish(PUB_FEED, b'1')
    PUB_FLAG = False


def lockStatus_cb(topic, msg):
    global LOCK_FLAG
    print(msg)
    if LOCK_FLAG and msg == b'1':
        unlock()
    if not LOCK_FLAG and msg == b'0':
        lock()


def lock():
    global LOCK_FLAG
    global MOTOR_DONE
    global P1A
    global P2A
    global P_EN
    print('locking')
    # start the motor for lock
    motorForward(P1A, P2A, P_EN)
    while not MOTOR_DONE:
        pass
        # do nothing here, just waiting for intterupt
    # stop motor
    motorStop(P1A, P2A, P_EN)
    MOTOR_DONE = False
    LOCK_FLAG = True


def unlock():
    global LOCK_FLAG
    global MOTOR_DONE
    global P1A
    global P2A
    global P_EN
    print('unlocking')
    # start the motor for unlock
    motorBackward(P1A, P2A, P_EN)
    while not MOTOR_DONE:
        pass
        # do nothing here, just waiting for intterupt
    # stop motor
    motorStop(P1A, P2A, P_EN)
    MOTOR_DONE = False
    LOCK_FLAG = False


def motorForward(p1, p2, pEN):
    pEN.value(0)
    p1.value(1)
    p2.value(0)
    pEN.value(1)


def motorBackward(p1, p2, pEN):
    pEN.value(0)
    p1.value(0)
    p2.value(1)
    pEN.value(1)


def motorStop(p1, p2, pEN):
    pEN.value(0)
    p1.value(0)
    p2.value(0)


def init(myMqttClient, feedURL, username, key, feed):
    global C
    global P5, P4
    global PUB_FEED
    PUB_FEED = feed
    print('motor test')
    motorForward(P1A, P2A, P_EN)
    time.sleep(0.5)
    motorBackward(P1A, P2A, P_EN)
    time.sleep(0.5)
    motorStop(P1A, P2A, P_EN)
    print('end motor test')

    C = MQTTClient(myMqttClient, feedURL, 0, username, key)
    C.set_callback(lockStatus_cb)
    C.connect()
    C.subscribe(feed)

    P5.irq(handler=setP5Flag, trigger=Pin.IRQ_FALLING)
    P4.irq(handler=setP4Flag, trigger=Pin.IRQ_FALLING)


def run():
    global C
    global PUB_FLAG
    while 42:
        C.check_msg()
        if PUB_FLAG:
            pubStatus(C)
