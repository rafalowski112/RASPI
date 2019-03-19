#------------------------------------------------------------------------------$
# SEKWENCJA POWITALNA
#------------------------------------------------------------------------------$
import RPi.GPIO as GPIO
from time import *

GPIO.setwarnings(False)

sensor=17
blue=4
red=2
buzz=21

GPIO.setmode(GPIO.BCM)
GPIO.setup(blue,GPIO.OUT)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(buzz,GPIO.OUT)

#------------------------------------------------------------------------------$

GPIO.output(blue,1)
GPIO.output(red,1)
GPIO.output(buzz,1)
sleep(0.2)
GPIO.output(blue,0)
GPIO.output(red,0)
GPIO.output(buzz,0)
sleep(0.2)
GPIO.output(blue,1)
GPIO.output(red,1)
GPIO.output(buzz,1)
sleep(0.2)
GPIO.output(blue,0)
GPIO.output(red,0)
GPIO.output(buzz,0)

#------------------------------------------------------------------------------$
