import sensor
import image
import lcd
import time
from fpioa_manager import *
from machine import I2C
from Maix import I2S, GPIO
from board import board_info
from pmu import axp192

pmu = axp192()
#enables the on/off (sleep) button
pmu.enablePMICSleepMode(True)

lcd.init(freq=15000000)
lcd.rotation(2)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)

try:
    img = image.Image("/sd/logoNEW.jpg")
    lcd.display(img)
except:
    lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Cannot find logo.jpg", lcd.WHITE, lcd.RED)

sensor.run(1)
dark_threshold   = (0, 19, -118, 127, -128, 127) #<-dark (39, 68, 50, 2, 102, -61) skin
while True:
    img=sensor.snapshot()
    blobs = img.find_blobs([dark_threshold])
    if blobs:
        for b in blobs:
            #tmp=img.draw_rectangle(b[0:4],color=(0,100,100), fill=False)
            if b.density() > 1 and b.w() > 150 and b.h() > 150:
                tmp=img.draw_rectangle(b[0:4],color=(0,100,100), fill=False)
                tmp=img.draw_string(b[0], b[4], str(b.density()), color=(0,128,0), scale=1)
                tmp=img.draw_cross(b[5], b[6])
                c=img.get_pixel(b[5], b[6])
                print(str(b.density())+" size:"+str(b.w())+" "+str(b.h()))
    lcd.display(img)
