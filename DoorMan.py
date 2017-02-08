from machine import Pin
from umqtt.simple import MQTTClient

class DoorMan:
    #flags for controlling door status
    flag4 = None
    flag5 = None
    lockFlag = False
    pubFlag = False
    motorDone = False

    #pin definitions
    p4 = Pin(4, Pin.IN, Pin.PULL_UP)
    p5 = Pin(5, Pin.IN, Pin.PULL_UP)
    p1A = Pin(12, Pin.OUT)
    p2A = Pin(13, Pin.OUT)
    pEN = Pin(14, Pin.OUT)

    def lockStatus_cb(self, topic, msg):
        print(msg)
        if self.lockFlag and msg ==b'1':
            self.unlock()
        if not self.lockFlag and msg ==b'0':
            self.lock()

    def setP4Flag(self, p):
        if p.value() == 0:
            self.flag4 = 1
            if self.flag5 == 1:
                #print('unlocking manually')
                self.lockFlag = False
                self.flag4 = 0
                self.flag5 = 0
                self.pubFlag = True
                self.motorDone = True

    def setP5Flag(self, p):
        if p.value() == 0:
            self.flag5 = 1
            if self.flag4 == 1:
                #print('locking manually')
                self.lockFlag = True
                self.flag4 = 0
                self.flag5 = 0
                self.pubFlag = True
                self.motorDone = True

    def pubStatus(c):
        if self.lockFlag:
            #print('publish locked')
            c.publish(feed,b'0')
        if not self.lockFlag:
            #print('publish unlocked')
            c.publish(feed,b'1')
        self.pubFlag = False

    def lock(self):
        #print('locking')
        #start the motor for lock
        self.motorForward()
        while not self.motorDone:
            pass
            # do nothing here, just waiting for intterupt
        #stop motor
        self.motorStop()
        self.motorDone = False
        self.lockFlag = True

    def unlock():
        #print('unlocking')
        #start the motor for unlock
        self.motorBackward()
        while not self.motorDone:
            pass
            # do nothing here, just waiting for intterupt
        #stop motor
        self.motorStop()
        self.motorDone = False
        self.lockFlag = False

    def motorForward(self):
        self.pEN.value(0)
        self.p1A.value(1)
        self.p2A.value(0)
        self.pEN.value(1)

    def motorBackward(self):
        self.pEN.value(0)
        self.p1A.value(0)
        self.p2A.value(1)
        self.pEN.value(1)

    def motorStop(self):
        self.pEN.value(0)
        self.p1A.value(0)
        self.p2A.value(0)

    def run(self):
        while(1):
            self.c.check_msg()
            if self.pubFlag:
                self.pubStatus(self.c)

    def __init__(self, myMqttClient, feedURL, username, key, feed):

        self.c =MQTTClient(myMqttClient,feedURL,0,username,key)
        self.c.set_callback(self.lockStatus_cb)
        self.c.connect()
        self.c.subscribe(feed)

        self.p5.irq(handler=self.setP5Flag, trigger=Pin.IRQ_FALLING)
        self.p4.irq(handler=self.setP4Flag, trigger=Pin.IRQ_FALLING)
