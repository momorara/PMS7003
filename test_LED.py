
#!/usr/bin/python

"""
###########################################################################
# LEDを on off

#Filename      :test_LED.py

LEDを点滅させます。

############################################################################
"""

import pigpio
import time

LED1 = 17
led = pigpio.pi()
# 出力設定
led.set_mode(LED1, pigpio.OUTPUT)


for _ in range(5):
    led.write(LED1, 1) # LED点灯
    time.sleep(0.5)
    led.write(LED1, 0) # LED消灯
    time.sleep(0.1)
