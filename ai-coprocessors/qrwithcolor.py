import sensor
import image
import lcd
import time
from fpioa_manager import fm
from machine import UART

fm.register(15, fm.fpioa.UART2_TX)
fm.register(7, fm.fpioa.UART2_RX)
uart_B = UART (UART.UART2, 115200, 8, None, 1, timeout = 1000, read_buf_len = 4096)
print('start UART B')
uart_B.write('UART B START \n\r')
clock = time.clock()
lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(1)
sensor.set_hmirror(1) # set hmirror if can not recognize qr code
sensor.skip_frames(30)
print('start qr')
green_threshold   = (0,   80,  -70,   -10,   -0,   30)
while True:
    clock.tick()
    img = sensor.snapshot()
    res = img.find_qrcodes()
    fps = clock.fps()
    if len(res) > 0:
        img.draw_string(2,2, res[0].payload(), color=(0,128,0), scale=2)
        print(res[0].payload())
        img.draw_rectangle(res[0].x(),res[0].y(),res[0].w(),res[0].h(),color=(255,1,1))
        print(res[0])
        uart_B.write(str(res[0]))        
    blobs = img.find_blobs([green_threshold])
    if blobs:
        for b in blobs:
            tmp=img.draw_rectangle(b[0:4])
            tmp=img.draw_cross(b[5], b[6],color=(255,1,1))
            c=img.get_pixel(b[5], b[6])
            #print(b.area())
    lcd.display(img)
