import math
import machine
import sys
import time
import uos
import os
import sensor
import image
import lcd
import KPU as kpu
import utime
import ubinascii
import gc
import uerrno
from Maix import utils
from Maix import GPIO
from machine import UART
from board import board_info
from fpioa_manager import *

time.sleep(0.5) # Delay for few seconds - EVERYTHING must be under 410 lines of code
lcd.init()
lcd.clear((255,206,0))
lcd.display(image.Image("/sd/oc.jpg").draw_rectangle(0,0,320,30, color=(0,0,0), fill=True).draw_string(50, 1, "GATEBOT BOOTUP", color=(5,250,0), scale=2))
but_stu = 1
fm.register(board_info.LED_R, fm.fpioa.GPIO0)
fm.register(board_info.LED_G, fm.fpioa.GPIO1)
fm.register(board_info.LED_B, fm.fpioa.GPIO2)
led_r=GPIO(GPIO.GPIO0,GPIO.OUT)
led_r.value(1)
led_g=GPIO(GPIO.GPIO1,GPIO.OUT)
led_g.value(1)
led_b=GPIO(GPIO.GPIO2,GPIO.OUT)
led_b.value(1)
arrow_pin_up = 3
arrow_pin_down = 5
arrow_pin_left = 4
arrow_pin_right = 6
key_pin=16 # 设置按键引脚 FPIO16
fpioa = FPIOA()
fpioa.set_function(key_pin,FPIOA.GPIO7)
key_gpio=GPIO(GPIO.GPIO7,GPIO.IN)
#START KEY ARROW
fpioa.set_function(arrow_pin_up,FPIOA.GPIO3)
up_gpio=GPIO(GPIO.GPIO3,GPIO.IN,GPIO.PULL_UP)
fpioa.set_function(arrow_pin_down,FPIOA.GPIO4)
down_gpio=GPIO(GPIO.GPIO4,GPIO.IN,GPIO.PULL_UP)
fpioa.set_function(arrow_pin_left,FPIOA.GPIO5)
left_gpio=GPIO(GPIO.GPIO5,GPIO.IN,GPIO.PULL_UP)
fpioa.set_function(arrow_pin_right,FPIOA.GPIO6)
right_gpio=GPIO(GPIO.GPIO6,GPIO.IN,GPIO.PULL_UP)
#END KEY ARROW
last_key_state = 1
last_keyup_state = 1
last_keydown_state = 1
last_keyright_state = 1
last_keyleft_state = 1
#uart
fm.register(20, fm.fpioa.UART2_TX, force=True)
fm.register(21, fm.fpioa.UART2_RX, force=True)
fm.register(22, fm.fpioa.UART1_TX, force=True)
fm.register(23, fm.fpioa.UART1_RX, force=True)
uart_B = UART(UART.UART2, 115200, 8, None, 1, timeout = 120, read_buf_len = 4096)
uart_C = UART(UART.UART1, 115200, 8, None, 1, timeout = 1000, read_buf_len = 8192)
uart_B.write('start')
#fix
#SERVO
key_threezero = 15 #10
fpioa.set_function(key_threezero,FPIOA.GPIOHS15) #10
servo_gpio=GPIO(GPIO.GPIOHS15,GPIO.OUT) #10
#servo timer & PWM setting frq80 duty9 rangeofmivement from 5 to 18 [0degrees is 5]
serv_tim = machine.Timer(machine.Timer.TIMER0, machine.Timer.CHANNEL0, mode = machine.Timer.MODE_PWM)
servo_zero = machine.PWM(serv_tim, freq = 80, duty = 10, pin = key_threezero, enable = False)
servo_zero.enable()
#key
key_pressed=0 # 初始化按键引脚 分配GPIO7 到 FPIO16
dir_pressed=0
menuenabled=False
menu_position = 0

def check_key(): # 按键检测函数，用于在循环中检测按键是否按下，下降沿有效
    global last_key_state
    global key_pressed
    global dir_pressed
    global last_keyup_state
    global last_keydown_state
    global last_keyright_state
    global last_keyleft_state
    global menuenabled
    global menu_position
    global debugview
    val=key_gpio.value()
    if last_key_state == 1 and val == 0:
        key_pressed=1
        led_g.value(0)
    else:
        key_pressed=0
        led_g.value(1)
    if last_keyup_state == 1 and up_gpio.value() == 0:
        led_b.value(0)
        dir_pressed = 1
        menuenabled = True
    elif menuenabled == False and down_gpio.value() == 0:
        debugview = True
    elif last_keydown_state == 1 and down_gpio.value() == 0:
        led_r.value(0)
        dir_pressed = 1
        menuenabled = False
        menu_position = 0
    elif last_keyright_state == 1 and right_gpio.value() == 0:
        led_g.value(0)
        dir_pressed = 1
    elif last_keyleft_state == 1 and left_gpio.value() == 0:
        led_g.value(0)
        led_b.value(0)
        dir_pressed = 1
    else:
        led_r.value(1)
        led_g.value(1)
        led_b.value(1)
        dir_pressed = 0
    last_keyup_state = up_gpio.value()
    last_keydown_state = down_gpio.value()
    last_keyright_state = right_gpio.value()
    last_keyleft_state = left_gpio.value()
    last_key_state = val

def findMaxIDinDir(dirname):
    larNum = -1
    try:
        dirList = uos.listdir(dirname)
        for fileName in dirList:
            currNum = int(fileName.split(".jpg")[0])
            if currNum > larNum:
                larNum = currNum
        return larNum
    except:
        return 0

def findMaxNum(fname):
    maxNum = -1
    try:
        drList = uos.listdir(fname)
        for fileName in drList:
            splitnumb = fileName.split(".bin")
            currNum = splitnumb[0].split("printbinary")
            currNumb = int(currNum[1])
            currNum.clear()
            splitnumb.clear()
            if currNumb > maxNum:
                maxNum = currNumb
        return maxNum
    except:
        return 0

def prntime(ms):
    s=ms/1000
    m,s=divmod(s,60)
    h,m=divmod(m,60)
    d,h=divmod(h,24)
    return d,h,m,s

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_gain(1)
sensor.set_auto_exposure(1)
sensor.set_brightness(0)
sensor.set_saturation(0)
sensor.set_contrast(0)
#sensor.skip_frames(5)
sensor.set_hmirror(1) #设置摄像头镜像
sensor.set_vflip(1)   #设置摄像头翻转
sensor.run(1)
#task = kpu.load(0x300000) # you need put model(face.kfpkg) in flash at address 0x300000
task = kpu.load("/sd/facedetect.kmodel")
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
if not "temp" in os.listdir("/sd/"): os.mkdir("/sd/temp/") # Make a temp directory
f= open("/sd/printoutput.txt","a+")
f.write("new boot \n\r")
f.close()
pixelchange = []
pixch=0
green_threshold = (0,80,-70,-10,-0,30)
taskkp = kpu.load("/sd/model/KP.smodel")
taskfe = kpu.load("/sd/model/FE.smodel")
record_ftr=[] #空列表 用于存储当前196维特征
record_ftrs=[bytearray(b'\xe8\x135"\xca\xf5\x0f\xd0\xd2\t\xf9\xe4\x0b\xf0\x03\x17\xfa\xe4\xb3\xe7E\xc2\x0f\x00\'\xfd\xe1\xfd2\xc2\xc5\xd3\x00\xd9%7\x06\xf9\x03\xe1\xda\x1b\xf8C\x18\x15\xe1\x07\xf9\x11\xd8*\xed\xbd\x0b\xcf\xed\x01\xf4\x07\x00\xd6\x00\xcd\x04\x05\xfa\xd9I\xd3\n\xf2)\xe5\x18\xd2\x0c\x11\x13\xde\x17\xe8\n2\xd9&\xe9\xe2\xf5\xeb\xe1\xf4\xaf\x17"\xf1$\xf9$\xb1.\xd0\xf4\x0f\'\x08\n\x1a"\xdd\xc3\xcf\xa7\x07\x1f\r\xc4\xd7\xdc\x05\x00\xfc0\x06\x1d>\x1b\xf9\xdf\x97\xcf5\xe5\xfa\x16\x04\x00\x1f\x07\x17\xf2\xde\xf1!\xec\x1e\xda\x00\xfd\xdc\xd8\x00\xa9\xdc$\x1d\xee\x12\xe9&\xec\xfc\x1cMP\x07\x03\xc6*0\xa9\xf0\xcc!\xe3\xf1\x05\nA\xed\x03\xeb\x173\xdc\xc8,\xfa\xf0\xcf\xc1\x03')] #空列表 用于存储按键记录下人脸特征， 可以将特征以txt等文件形式保存到sd卡后，读取到此列表，即可实现人脸断电存储。
#load last face data of ONICHAN
f = open("/sd/facedata/printbinary"+str(findMaxNum("/sd/facedata"))+".bin","rb")
with open("/sd/facedata/printbinary"+str(findMaxNum("/sd/facedata"))+".bin", "rb") as f:
    record_ftrs = [bytearray(f.read())]
names = ['Onii-chan', 'Mr.2', 'Mr.3', 'Mr.4'] 
dst_point = [(44,59),(84,59),(64,82),(47,105),(81,105)] #standard face key point position 标准正脸的5关键点坐标 分别为 左眼 右眼 鼻子 左嘴角 右嘴角
img_face=image.Image(size=(128,128))
try:
    currentImage = findMaxIDinDir("/sd/capture") + 1
except:
    currentImage = 0
    pass
timeout = 120000 #clock.tick() 40 minutes = 2 400 000 milliseconds
oldtimer = 0
scheduled_time = 120000
greetback = False
score = 0
key_pressed = 5
time.sleep(2)
imgv = 0
n = 0
pd = True
yolonum = findMaxIDinDir("/sd/yoloimages/")+1

#load the original face data from file into bytearray
def loadfacedata():
    f = open("/sd/facedata/printbinary"+str(findMaxNum("/sd/facedata"))+".bin","rb")
    with open("/sd/facedata/printbinary"+str(findMaxNum("/sd/facedata"))+".bin", "rb") as f:
        record_ftrs = [bytearray(f.read())]

#debug camera view 
debugview = False
loopchck = 5

#debug view over UART
def debugerview():
    global debugview
    global loopchck
    imgde = image.Image("/sd/videopic/idle_"+str(n)+".jpg", copy_to_fb=True)
    uart_B.write(" hexstart ")
    fl = open("/sd/printoutput.txt","a+")
    fl.write("Initial UART data transfer \n\r")
    fl.close()
    lcd.display(imgde.draw_string(40, 50, " TRANSFERING ", color=(0,0,0), scale=2))
    try:
        fi = open("/sd/temp/"+str(currentImage-1)+".jpg","rb")
        fullsize = len(fi.read())
        targetsize = 4
        fi.seek(0, 0)
        lcd.display(imgde.draw_string(2, 5, " TRANSFERING ", color=(0,0,0), scale=2))
        lcd.display(imgde.draw_string(2, 17, "4/"+str(fullsize), color=(0,0,0), scale=2))
        byte = fi.read(4) # 4 was optimal
        while len(byte):
            uart_B.write(str(ubinascii.hexlify(byte))+">")
            byte = fi.read(4)
            targetsize += 4
            time.sleep(0.1)
            lcd.display(image.Image("/sd/videopic/idle_"+str(n)+".jpg", copy_to_fb=True).draw_rectangle(0,0,150,30, color=(0,0,0), fill=True).draw_string(2, 1, str(targetsize)+"/"+str(fullsize), color=(5,250,0), scale=2))
        fi.close()
        uart_B.write(" hexend ")
    except:
        uart_B.write(" failed transfer ")
        fl = open("/sd/printoutput.txt","a+")
        fl.write("failed to transfer UART data \n\r")
        fl.close()

def seeotheritems():  #7second delay
    global taskfe
    global a
    global task
    global yolonum
    global anchor
    classes = ['aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
    anchored = (1.08, 1.19, 3.42, 4.41, 6.63, 11.38, 9.42, 5.11, 16.62, 10.52)
    kpu.deinit(taskfe)
    kpu.deinit(task)
    tasktw = kpu.load("/sd/model/20class.kmodel")
    uart_B.write(" loaded 20 ")
    kpu.init_yolo2(tasktw, 0.5, 0.3, 5, anchored)
    imgother = sensor.snapshot()
    imgother.pix_to_ai()
    detectcode = kpu.run_yolo2(tasktw, imgother)
    if detectcode:
        led_r.value(0)
        led_b.value(0)
        for i in detectcode:
            imgother = imgother.draw_rectangle(i.rect())
            for i in detectcode:
                imgother = imgother.draw_string(i.x(), i.y(), str(classes[i.classid()]), color=(255,250,250))
                imgother = imgother.draw_string(i.x(), i.y()+12, '%f1.3'%i.value(), color=(255,250,250))
                imgother.save("/sd/yoloimages/"+str(yolonum)+".jpg", quality=70)
                utime.sleep_ms(50)
                yolonum+=1
                uart_B.write(" |Yolo|> "+ str(classes[i.classid()]) +" <||")
                f= open("/sd/printoutput.txt","a+")
                f.write("Yolo detected: "+ str(classes[i.classid()]) +"\n\r")
                f.close()
    del(imgother)
    kpu.deinit(tasktw)
    del(tasktw)
    gc.collect()
    uart_B.write(" killed ")
    task = kpu.load("/sd/facedetect.kmodel")
    taskfe = kpu.load("/sd/model/FE.smodel")
    utime.sleep_ms(10)
    led_r.value(1)
    led_b.value(1)
    kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
    uart_B.write(" restarted ")

try:
    while(True):
        if debugview ==  True:
            #debugerview()
            seeotheritems()#TEST OTHER MODEL
            debugview = False
        check_key()
        if dir_pressed == 1:
            while(menuenabled):
                imgv = image.Image("/sd/videopic/idle_"+str(n)+".jpg", copy_to_fb=True)
                imgv = imgv.draw_rectangle(4,5,140,100, color=(0,0,0), fill=True)
                if last_keyright_state == 0 or menu_position == 2:
                    imgv = imgv.draw_rectangle(5,5,140,10, color=(0,240,0), fill=True)
                    menu_position = 2
                    binarraysize = len(record_ftrs)
                    if last_keyright_state == 0:
                        f = open("/sd/facedata/printbinary"+str(findMaxNum("/sd/facedata")+1)+".bin","wb+")
                        binarraysize = binarraysize-1
                        f.write(record_ftrs[binarraysize])
                        f.close()
                        f= open("/sd/printoutput.txt","a+")
                        f.write("Face vectors binaries saved :"+str(findMaxNum("/sd/facedata"))+"\n\r")
                        f.close()
                    imgv = imgv.draw_string(5, 30, str(binarraysize)+" "+str(findMaxNum("/sd/facedata")+1), color=(255,250,250), scale=2)
                if last_keyleft_state == 0  or menu_position == 1:
                    imgv = imgv.draw_rectangle(5,14,140,10, color=(0,240,0), fill=True)
                    if last_keyleft_state == 0:
                        debugerview()
                        imgv = imgv.draw_rectangle(5,14,140,10, color=(250,0,0), fill=True)
                    menu_position = 1
                imgv = imgv.draw_string(5, 5, "Save face data", color=(255,250,250), scale=1)
                imgv = imgv.draw_string(5, 15, "Send last IMG", color=(255,250,250), scale=1)
                lcd.display(imgv)
                check_key()
                utime.sleep_ms(80)
                n+=1
                if n >= 68:
                    n = 0
        now = time.ticks()
        img = sensor.snapshot()
        #find room movement by pixel color change
        pixelchange.append(img.get_pixel(122,188))
        if len(pixelchange) > 2 :
            o = 0
            pixch = len(pixelchange) - 2
            for u in pixelchange[pixch]:
                if abs(u - pixelchange[len(pixelchange)-1][o]) >= 20 :
                    led_g.value(0)
                    uart_B.write('| movement detected | \n\r')
                    utime.sleep_ms(10)#100 - 70
                else:
                    led_g.value(1)
                o += 1
        #end not blob
        if len(pixelchange) == 50:
            pixelchange.clear()
        code = kpu.run_yolo2(task, img)
        led_r.value(1)
        if time.ticks_diff(scheduled_time, now) > 0:
            pass
        elif time.ticks_diff(scheduled_time, now) < 0:
            if greetback == False:
                print(str(timeout)+" ms passed - greet when user returns ")
                uart_B.write(str(timeout)+" ms passed - greet when user returns | \n\r")
                greetback = True #scheduled_time = timeout+now
        #read_data = uart_C.readline()
        try:
            read_data = uart_C.read()
            dataout = str(read_data)
            if dataout != '' and dataout != 'None':
                dataout = str(read_data.decode('utf-8'))
                #jsonqr = ujson.loads(dataout)
                uart_B.write("UART2: "+dataout)
                #uart_B.write("UART2 read_data: "+read_data.decode("utf-8")+" \n\r")
                #uart_B.write(uart_C.readline())
        except Exception as e:
            uart_B.write(str(e))
        if code:
            for i in code:
                img.save("/sd/temp/"+str(currentImage)+".jpg", quality=80)
                img = img.draw_rectangle(i.rect())
                face=img.cut(i.x(),i.y(),i.w(),i.h())
                #servo movement 
                if i.x() < 106 :
                    if servo_zero.duty() == 14:
                        servo_zero.duty(10)
                    else:
                        servo_zero.duty(7)
                elif i.x() > 213 :
                    if servo_zero.duty() == 7:
                        servo_zero.duty(10)
                    else:
                        servo_zero.duty(14)
                else:
                    uart_B.write('| servo | \n\r') #frz
                #servo movement code end
                img = img.clear()
                img=face.resize(128,128)
                #img = img.draw_image(face, i.x(), i.y())
                del(face)
                a=img.pix_to_ai()
                fmap = kpu.forward(taskkp, img)
                plist=fmap[:]
                del(fmap)
                le=(0+int(plist[0]*128 - 10), 0+int(plist[1]*128))
                re=(0+int(plist[2]*128), 0+int(plist[3]*128)) 
                nose=(0+int(plist[4]*128), 0+int(plist[5]*128)) 
                lm=(0+int(plist[6]*128), 0+int(plist[7]*128)) 
                rm=(0+int(plist[8]*128), 0+int(plist[9]*128))
                img = img.draw_circle(le[0], le[1], 4)
                img = img.draw_circle(re[0], re[1], 4)
                img = img.draw_circle(nose[0], nose[1], 4)
                img = img.draw_circle(lm[0], lm[1], 4)
                img = img.draw_circle(rm[0], rm[1], 4)
                # calculate face feature vector
                scores = []
                fmap = kpu.forward(taskfe, img) # 计算正脸图片的196维特征值
                feature=kpu.face_encode(fmap[:])#获取计算结果
                kpu.fmap_free(fmap)
                del(plist)
                for j in range(len(record_ftrs)):
                    score = kpu.face_compare(record_ftrs[j], feature)
                    scores.append(score)
                max_score = 0
                index = 0
                for k in range(len(scores)): #迭代所有比对分数，找到最大分数和索引值
                    if max_score < scores[k]:
                        max_score = scores[k]
                        index = 0 #cross check with a different face model
                if max_score > 60 and max_score < 80:
                    uart_B.write(" 60-85 score \n\r")
                    f = open("/sd/facedata/printbinary13.bin","rb")
                    with open("/sd/facedata/printbinary13.bin", "rb") as f:
                        record_ftrs = [bytearray(f.read())]
                for j in range(len(record_ftrs)):
                    max_score = kpu.face_compare(record_ftrs[j], feature)
                if max_score > 80: # 如果最大分数大于85， 可以被认定为同一个人 to 76 frz
                    img = img.draw_string(0,0, ("%s :%2.1f" % (names[0], max_score)), color=(0,255,0),scale=2) # 显示人名 与 分数
                else:
                    img = img.draw_string(0,0, ("%s :%2.1f" % (names[1], max_score)), color=(0,255,0),scale=2)
                if key_pressed >= 1 :
                    key_pressed += 1
                    record_ftr = feature
                    record_ftrs.append(record_ftr)
                loadfacedata()
                if n != 0:
                    if math.fmod(n,2) == 0:
                        f= open("/sd/printoutput.txt","a+")
                        path = "/sd/capture/"+str(currentImage)+".jpg" #here
                        currentImage = currentImage+1
                        img.save(path)
                        time.sleep_ms(50)
                        uart_B.write("| saved image | \n\r")
                        f.write(str(i)+" picture: "+str(currentImage)+".jpg "+str(score)+" \n\r")
                        f.close()
                gc.collect()
                led_r.value(0)
                imgv = image.Image("/sd/videopic/idle_"+str(n)+".jpg", copy_to_fb=True)
                utime.sleep_ms(50)
                if greetback == True :
                    uart_B.write(" Welcome back onii-chan \n\r")
                    uart_B.write('%d days %d hours %d minutes %d seconds '%prntime(abs(time.ticks_diff(scheduled_time, now))))
                    scheduled_time = timeout+now #reset timer
                    imgv = image.Image("/sd/videopic/idle_"+str(n)+".jpg", copy_to_fb=True)
                    lcd.display(imgv.draw_string(0, 20, "Welcome back ", color=(255,0,0), scale=2))
                    greetback = False
                a = 0
                lcd.display(imgv.draw_string(0, 5, " pic: "+str(currentImage)+".jpg "+str(score), color=(255,250,250), scale=1))
                img = img.resize(100,100)
                lcd.display(imgv.draw_image(img,0,128))#a = img
                del(img)
                pd = False
        if pd == True:
            lcd.display(image.Image("/sd/videopic/idle_"+str(n)+".jpg", copy_to_fb=True))
            utime.sleep_ms(10)
        pd = True
        n+=1
        if n >= 68:
            n = 0
except Exception as x:
    a = kpu.deinit(taskfe)
    a = kpu.deinit(task)
    a = kpu.deinit(taskkp)
    sys.print_exception(x, file="/sd/error.txt")
    uart_B.write(str(x)+"  "+str(x.args[0]))
