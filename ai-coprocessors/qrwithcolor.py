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
dark_threshold   =  (39, 68, 50, 2, 102, -61) #<-skin (0, 19, -118, 127, -128, 127) <-dark
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
    blobs = img.find_blobs([dark_threshold])
    if blobs:
        for b in blobs:
            tmp=img.draw_rectangle(b[0:4],color=(0,100,100), fill=False)
            #if b.density() > 1 and b.w() > 150 and b.h() > 150:
            #    tmp=img.draw_rectangle(b[0:4],color=(0,100,100), fill=False)
            #    tmp=img.draw_string(b[0], b[4], str(b.density()), color=(0,128,0), scale=1)
            #    tmp=img.draw_cross(b[5], b[6])
            #    c=img.get_pixel(b[5], b[6])
            #    print(str(b.density())+" size:"+str(b.w())+" "+str(b.h()))
            #    uart_B.write('{ "desnsity":'+str(b.density())+' "bw:"'+str(b.w())+'"bh:"'+str(b.h())+' }')
            #print(b.area())
            if b.density() > 0.5 and b.w() > 50 and b.h() > 100:
                tmp=img.draw_rectangle(b[0:4])
                tmp=img.draw_cross(b[5], b[6],color=(255,1,1))
                c=img.get_pixel(b[5], b[6])
                print('{ "desnsity":'+str(b.density())+' , "bw":'+str(b.w())+' , "bh":'+str(b.h())+' }')
                uart_B.write('{ "desnsity":'+str(b.density())+' , "bw":'+str(b.w())+' , "bh":'+str(b.h())+' }')
    lcd.display(img)
