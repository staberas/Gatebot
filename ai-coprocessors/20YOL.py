import sensor,image,lcd,time,ujson
import KPU as kpu
from fpioa_manager import fm
from machine import UART

fm.register(15, fm.fpioa.UART2_TX)
fm.register(7, fm.fpioa.UART2_RX)
fm.register(6, fm.fpioa.UART1_TX)
fm.register(8, fm.fpioa.UART1_RX)
uart_B = UART (UART.UART2, 115200, 8, None, 1, timeout = 1000, read_buf_len = 4096)
uart_C = UART (UART.UART1, 115200, 8, None, 1, timeout = 1000, read_buf_len = 4096)
print('start UART B - reading mode')
uart_B.write('UART B START - reading mode \n\r')
uart_C.write('UART C START - push mode \n\r')
lcd.init(freq=15000000)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_vflip(1)
sensor.skip_frames(30)
sensor.run(1)
clock = time.clock()
classes = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
task = kpu.load(0x500000)
anchor = (1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52)
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
wt = 5
while(wt>0):
    time.sleep(1) # seconds
    wt -= 1
    print("starting in: "+ str(wt))
del wt
while(True):
    clock.tick()
    img = sensor.snapshot()
    code = kpu.run_yolo2(task, img)
    #print(clock.fps())
    read_data = uart_B.read()
    #qr = ujson.loads()
    try:
        if read_data != '' and read_data != None:
            qr = str(read_data.decode("utf-8"))
            jsonqr = ujson.loads(qr)
            a = img.draw_rectangle(jsonqr['x']+10,jsonqr['y'],jsonqr['w'],jsonqr['h'],lcd.RED)
            print(qr)
            uart_C.write(qr+"\n\r")
        #print("Failed JSON decode")
    except:
        print(" ")
    if code:
        for i in code:
            a = img.draw_rectangle(i.rect())
            a = lcd.display(img)
            for i in code:
                #img.draw_string(i.x(), i.y(), classes[i.classid()], lcd.RED, lcd.WHITE)
                #a=img.draw_string(i.x(), i.y()+12, '%.3f'%i.value(), lcd.RED, lcd.WHITE)
                #jsoni = ujson.loads()
                print(i)
                uart_C.write(str(i)+"\n\r")
                #print(classes[i.classid()])
    else:
        a = lcd.display(img)
a = kpu.deinit(task)
