#script for a502 sensor
#libraries can very depending on what hardware is being used
#this script is designed for pi pico using micropython, an ilia9341 LCD
#a vl6180x tof sensor, and a502 FSR
from time import sleep
from ili9341 import Display
from machine import Pin, SPI, I2C, ADC
from sys import modules
from xglcd_font import XglcdFont
import _thread
import vl6180x as tof
#Pins can be modified as needed
font = XglcdFont('/EspressoDolce18x24.c', 18, 24)
#fsr set to adc pin 26
FSR = ADC(Pin(26))
#values
alpha = 0.5
voltage = 3/65535
initvalues = FSR.read_u16()
fsrP=1
count = 0
stop = 0
weight = 0
white = 0xFFFFFF
black = 0x000000
#boundries for drawin
starterx = 2
startery = 230
#5 buttons, but this is just for a 5 way nav switch
up = Pin(5, Pin.IN, Pin.PULL_UP)
down = Pin(6, Pin.IN, Pin.PULL_UP)
left = Pin(13, Pin.IN, Pin.PULL_UP)
right = Pin(14, Pin.IN, Pin.PULL_UP)
bb = Pin(15, Pin.IN, Pin.PULL_UP)
#this is for tof sensor, uncomment this if tof works
#please note program will fail if you uncomment this without a tof sensor
#i2c = I2C(0,scl = Pin(1), sda = Pin(0),freq = 4000000)
#sensor = tof.Sensor(i2c)
#Baud rate of 40000000 seems about the max
#setting up display, add miso if you want to read data from lcd
spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
display = Display(spi, dc=Pin(16), cs=Pin(18), rst=Pin(17),width=320, height=240, rotation=90)
#this function is for user interaction, user will first draw the graph
#then the real graph will be drawn
def intros(starterx,startery):
    print("in intro")
    while(1):        
        if not up.value():
            print("up")
            startery -= 2
            if (startery <0):
                startery = 239
            display.draw_pixel(starterx,startery,0xFFFF00)
            sleep(0.1)
        elif not down.value():
            print("right")
            starterx +=2
            display.draw_pixel(starterx,startery,0xFFFF00)
            if (starterx >319):
                starterx = 0
            sleep(0.1)
        elif not left.value():
            print("down")
            startery +=2
            if (startery >239):
                startery = 0
            display.draw_pixel(starterx,startery,0xFFFF00)
            sleep(0.1)
        elif not right.value():
            print("push")
            sleep(0.1)
            break
        elif not bb.value():
            print("left")
            starterx -=2
            if (starterx <0):
                starterx = 319
            display.draw_pixel(starterx, startery,0xFFFF00)
            sleep(0.1)
#creating background for LCD
display.fill_rectangle(0, 0, 320, 240, 0x040273)
display.fill_rectangle(5,5, 310, 230, 0x000000)
display.draw_text8x8(30, 30, "Team Make-N-Break(TM Pending)", white)
display.draw_text8x8(80, 40, "Introduces the...", white)
sleep(0.5)
display.draw_text(65, 70, "TEST RIG 9000", font, white)
sleep(2)
display.clear()
display.draw_text(2, 70, "Create your own graph", font, white)
display.draw_text(2, 140, "using the joystick!", font, white)
display.draw_text(2,200, "Press joystick to end :)",font,white)
sleep(2)
display.clear()
plot =2
for x in range(46):
    display.draw_line(2,230-plot,6,230-plot, white)
    plot+=5
#uncomment this to have range zerod
#starterRange = sensor.range()
#creation of data csv file
data = open("data.csv", "w")
display.draw_line(2, 2, 2, 230, 0xFFFFFF)#(x1,y1,x2,y2,color)
display.draw_line(2,230,319, 230, 0xFFFFFF)
plot = 2

display.draw_text8x8(220,232,"Time",white)
display.draw_text8x8(4,2,"Force",white, rotate = 270)
#intro function
intros(starterx,startery)
#main loop where the magic happens
#each pixel is values as 1
while(1):
    values = FSR.read_u16()
    initvalues = alpha*initvalues+(1-alpha)*values
    volt = initvalues*voltage
    #uncomment this for displacement reading
    #displacement = starterRange-sensor.range()
    #you can print it to terminal if wanted
    #print("Displacement: ",displacement*0.0393701)
    #weight equations based on calibration and creating 3rd order polynomials from 0-62 and 62-194lbs
    #this was calibrated while the sensor was in the clamp
    #this one is for 0-62lbs
    if (volt <= 0.410245):
        cal = 3546.4*(volt**3)-2887.8*(volt**2)+899.21*volt-63.4
    #this is for 62-194
    if (volt > 0.410245):
        cal = 361858*(volt**3)-484010*(volt**2)+215773*volt-31981
    weight = cal
    voltval = initvalues*voltage
    #print("weight: ", weight, "voltage:",initvalues*voltage)
    #rounded so it doesnt take up a lot of lcd space
    display.draw_text8x8(100, 10, str(round(weight,2))+ "(lbs) "+str(round(voltval,3)) + "(V)", white)
    #this is for the graph
    #displacement *= 10
    #inch = displacement*0.0393701
    #print(inch)
    #inches = int(inch)
    weight = int(weight)
    #plotting, start y axis near the limit since top left is 0,0
    display.draw_pixel(2+count,230-(weight-1),0xFFFFFF)
    #display.draw_text8x8(100, 20, str(round(inch,2)) +"(in)", white)
    #inch = displacement*0.0393701
    #you can uncomment #+str to have that data inputted into a csv, have "," for it can go into another cell
    data.write(str(weight)+","+str(voltval)+"\n")#+str(inch)+"\n")
    sleep(0.2)
    #using this as time variable
    count+=1
    #end loop, and save data afterwards
    if not right.value():
        display.clear()
        display.draw_text(2, 70, "Thank you for using the", font, white)
        display.draw_text(60, 110, "TEST RIG 9000", font, white)
        display.draw_text8x8(60, 140, "Data saved.",white)
        break
data.close()


