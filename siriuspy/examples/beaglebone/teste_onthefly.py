from PRUserial485 import *
from comandos import *
import time

a = []
b = []
c = []
d = []


for i in range(4000):
	a.append(float(i)/1000.0)
	b.append(float(i)/2000.0)
	c.append(2.0 - float(i)/2000.0)
	d.append(4.0 - float(i)/1000.0)

a[3999] = 0.0
b[3999] = 0.0

PRUserial485_open(6,"M")

TurnOff(5)
TurnOff(6)

time.sleep(3)

ConfigModoSincrono(5)
ConfigModoSincrono(6)

PRUserial485_curve(a,a,a,a,0)



print "Starting SYNC..."
PRUserial485_sync_start(0xCE,100,0x05)
PRUserial485_curve(d,d,d,d,1)
PRUserial485_set_curve_block(1)

time.sleep(5)
'''
while True:
	#a = raw_input()
	time.sleep(2)
	print "Escrevendo B bloco 1 e escolhendo-o"
	PRUserial485_curve(b,b,b,b,1)
	PRUserial485_set_curve_block(1)
	time.sleep(2)	
	#a = raw_input()
	print "Escrevendo C bloco 2 e escolhendo-o"
	PRUserial485_curve(c,c,c,c,2)
	PRUserial485_set_curve_block(2)
	#a = raw_input()
	time.sleep(2)
	print "Escrevendo D bloco 1 e escolhendo-o"
	PRUserial485_curve(d,d,d,d,1)
	PRUserial485_set_curve_block(1)
	#a = raw_input()
	time.sleep(2)
	print "Escrevendo A bloco 2 e escolhendo-o"
	PRUserial485_curve(a,a,a,a,2)
	PRUserial485_set_curve_block(2)

	print PRUserial485_read_pulse_count_sync()
'''
while True:

#	ReadGroup(5)
	time.sleep(0.5)
	print PRUserial485_read_pulse_count_sync()
	print PRUserial485_read_curve_pointer()
	print "\n"

		
