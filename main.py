import doorLock

myMqttClient = "lock-mqtt-client"  # can be anything unique
adafruitIoUrl = "io.adafruit.com"
adafruitUsername = "athulus"  # can be found at "My Account" at adafruit.com
adafruitAioKey = "7f7206bab2a145429298cdd4cc2b6cc4"  # can be found by clicking on "VIEW AIO KEYS" when viewing an Adafruit IO Feed
feed ='athulus/f/doorStatus'

doorLock.init(myMqttClient, adafruitIoUrl, adafruitUsername, adafruitAioKey,feed)

doorLock.run()
