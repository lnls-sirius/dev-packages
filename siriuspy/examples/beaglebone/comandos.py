from PRUserial485 import *
import time, datetime
import sys
import os
import struct


def print_byte_list(byte_list):
    sys.stdout.write(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S.%f")[:-4] + " - Resposta do controlador: ")
    i = 0
    while (i < len(byte_list)):
        if (i == len(byte_list) - 1):
            sys.stdout.write("{0:01x}".format(ord(byte_list[i])).upper())
        else:
            sys.stdout.write("{0:01x}".format(ord(byte_list[i])).upper() + " ")
        i += 1
    sys.stdout.write("\n")
    sys.stdout.flush()


def includeChecksum(string):
    counter = 0
    i = 0
    while (i < len(string)):
        counter += ord(string[i])
        i += 1
    counter = (counter & 0xFF)
    counter = (256 - counter) & 0xFF
    return(string + [chr(counter)])



def verifyChecksum(string):
    counter = 0
    i = 0
    while (i < len(string)):
        counter += ord(string[i])
        i += 1
    counter = (counter & 0xFF)
    return(counter)


def SetIx4(fonte,i1,i2,i3,i4):
	setIx4_command = [0x50,0x00,0x11,0x11]
	setIx4_command_char = []
    	setIx4_command_char.append(chr(fonte))

	current_int = struct.unpack('<I', struct.pack('<f', i1))[0]
	for i in range (0,4):
		setIx4_command.append(int(current_int%256))
		current_int = current_int/256

	current_int = struct.unpack('<I', struct.pack('<f', i2))[0]
	for i in range (0,4):
		setIx4_command.append(int(current_int%256))
		current_int = current_int/256

	current_int = struct.unpack('<I', struct.pack('<f', i3))[0]
	for i in range (0,4):
		setIx4_command.append(int(current_int%256))
		current_int = current_int/256

	current_int = struct.unpack('<I', struct.pack('<f', i4))[0]
	for i in range (0,4):
		setIx4_command.append(int(current_int%256))
		current_int = current_int/256


    
	for i in range (0,len(setIx4_command)):
		setIx4_command_char.append(chr(setIx4_command[i]))

	PRUserial485_write(includeChecksum(setIx4_command_char), 100);
        resp = PRUserial485_read()
	print_byte_list(resp)
	return



def Read_counterSetx4(fonte):
	PRUserial485_write(includeChecksum([chr(fonte)] + ['\x10','\x00','\x01','\x04']),100)
	resp = PRUserial485_read()
	print_byte_list(resp)
	if(verifyChecksum(resp) == 0):
		if (len(resp) == 9):
			val = struct.unpack("<f", "".join(resp[4:-1]))[0]
			return val


def Read_MessageError(fonte):
	PRUserial485_write(includeChecksum([chr(fonte)] + ['\x10','\x00','\x01','\x32']),100)
	resp = PRUserial485_read()
	print_byte_list(resp)
	if(verifyChecksum(resp) == 0):
		if (len(resp) == 6):
			val = ord(resp[4])
			return val

def Clear_MessageError(fonte):
	PRUserial485_write(includeChecksum([chr(fonte)] + ['\x20','\x00','\x01','\x32','\x00']),100)
	resp = PRUserial485_read()
	print_byte_list(resp)
	return



def ResetWfmRef(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ['\x50','\x00','\x01','\x13']),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	if(verifyChecksum(resp) == 0):
                if (len(resp) == 6):
                        return 0
		else:
			return -1
	else:
		return -1


def ResetInterlock(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x50", "\x00", "\x01", "\x06"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return


def TurnOn(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x50", "\x00", "\x01", "\x00"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return

def TurnOff(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x50", "\x00", "\x01", "\x01"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return


def CloseControlLoop(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x50", "\x00", "\x01", "\x03"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return


def ClearGroups(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x32", "\x00", "\x00"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return


def CreateGroup(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x30", "\x00", "\x02", "\x02", "\x03"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return


def ReadGroup(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x12", "\x00", "\x01", "\x03"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return resp


def SlowRef(fonte):
        PRUserial485_write(includeChecksum([chr(fonte)] + ["\x50", "\x00", "\x03", "\x04", "\x00", "\x00"]),100)
        resp = PRUserial485_read()
	print_byte_list(resp)
	return



def ConfigModoSincrono(fonte):
	#print("(1/7) Reset WfmRef...")
	#ResetWfmRef(fonte)
	#time.sleep(0.5)
	print("(2/7) Reset Interlock...")
	ResetInterlock(fonte)
	time.sleep(0.5)
	print("(3/7) Turn On...")
	TurnOn(fonte)
	time.sleep(0.5)
	print("(4/7) Fecha malha...")
	CloseControlLoop(fonte)
	time.sleep(0.5)
	print("(5/7) Limpa grupos...")
	ClearGroups(fonte)
	time.sleep(0.5)
	print("(6/7) Cria grupo...")
	CreateGroup(fonte)
	time.sleep(0.5)
	print("(7/7) Modo SlowRef...")
	SlowRef(fonte)
	time.sleep(0.5)

	return


def LoadCurve(filenames): # [curva1.txt, curva2.txt, curva3.txt, curva4.txt]

    curves ={
        0   :   [],
        1   :   [],
        2   :   [],
        3   :   []
        }

    for i in range(4):
        f = open(filenames[i],"r")
        r = f.readlines()
        f.close()

        for z in range (len(r)):
            curves[i].append(float(r[z]))

    PRUserial485_curve(curves[0],curves[1],curves[2],curves[3])
    return
