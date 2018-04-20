#!/usr/bin/python
# -*- coding: utf-8 -*-


# IOC.py
# Software para testes das fontes FBP pelo pessoal do grupo FAC.

# Executar: "python IOC.py B1" para o bastidor 1 ou "python IOC.py B2" para o bastidor 2.

# Autor: Eduardo Pereira Coelho


# Módulos necessários

import datetime
from pcaspy import Driver, Alarm, Severity, SimpleServer
import threading
import socket
import struct
import sys
import time

if (sys.version_info[0] == 2):
    from PRUserial485 import *
    from Queue import Queue
else:
    from PRUserial485.PRUserial485 import *
    from queue import Queue

# Dicionários com os nomes das fontes, seus endereços seriais, novos modos de operação e curvas de rampa

if (len(sys.argv) == 1):
    sys.stdout.write("Executar \"python IOC.py B1\" ou \"python IOC.py B2\". Faltou o argumento.\n")
    exit()

if (sys.argv[1] == "B1"):
    power_supplies = {"BO-01U:PS-CH" : 1, "BO-01U:PS-CV" : 2 }
    curves = { 1 : [0.0] * 4000, 2 : [0.0] * 4000 }
    new_op_modes = {"BO-01U:PS-CH" : None, "BO-01U:PS-CV" : None }
    CRATE = 1 
elif (sys.argv[1] == "B2"):
    power_supplies = { "BO-03U:PS-CH" : 5, "BO-03U:PS-CV" : 6}
    curves = { 5 : [0.0] * 4000, 6 : [0.0] * 4000 }
    new_op_modes = {"BO-03U:PS-CH" : None, "BO-03U:PS-CV" : None }
    CRATE = 2
else:
    sys.stdout.write("Configuração desconhecida de bastidor.\n")
    sys.stdout.write("Por favor execute \"python IOC.py B1\" ou \"python IOC.py B2\".\n")


# Define as PVs que serão servidas pelo programa

PVs = {}

PVs ["SerialNetwork" + str(CRATE) + ":Sync"] = { "type" : "enum", "enums" : ["Off", "On"] }
PVs ["SerialNetwork" + str(CRATE) + ":Count"] = { "type" : "int" }

for ps_name in power_supplies.keys():

    PVs[ps_name + ":Current-Mon"] = { "type" : "float", "prec" : 6, "unit" : "A" }
    PVs[ps_name + ":Current-SP"] = { "type" : "float", "prec" : 6, "unit" : "A" }
    PVs[ps_name + ":Current-RB"] = { "type" : "float", "prec" : 6, "unit" : "A" }
    PVs[ps_name + ":CurrentRef-Mon"] = { "type" : "float", "prec" : 6, "unit" : "A" }
    PVs[ps_name + ":Intlk-Mon"] = { "type" : "int" }
    PVs[ps_name + ":IntlkLabels-Cte"] = { "type" : "string", "count" : 8, "value" : ["Overtemperature on module", "Overcurrent on load", "Overvoltage on load", "Overvoltage on DC-Link", "Undervoltage on DC-Link", "DC-Link input relay fail", "DC-Link input fuse fail", "Fail on module drivers"] }
    PVs[ps_name + ":OpMode-Sel"] = { "type" : "enum", "enums" : ["Off", "Interlock", "Initializing", "SlowRef", "SlowRefSync", "FastRef", "RmpWfm", "MigWfm", "Cycle"], "value" : 3 }
    PVs[ps_name + ":OpMode-Sts"] = { "type" : "enum", "enums" : ["Off", "Interlock", "Initializing", "SlowRef", "SlowRefSync", "FastRef", "RmpWfm", "MigWfm", "Cycle"], "value" : 3 }
    PVs[ps_name + ":Reset-Cmd"] = { "type" : "int" }
    PVs[ps_name + ":WfmData-SP"] = { "type" : "float", "count": 4000, "prec" : 6, "value" : [0.0] * 4000 }

# Sufixos das PVs de leitura das fontes

pv_suffixes = [":Current-Mon", ":Current-RB", ":CurrentRef-Mon", ":Intlk-Mon", ":OpMode-Sts"]

# Função que retorna uma estampa de tempo (usada pelas mensagens de log)

def time_string():
    return(datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S.%f - "))

# Procedimento que formata como string uma sequência de bytes (usado para debug)

def format_byte_list(byte_list):
    i = 0
    answer = ""
    while (i < len(byte_list)):
        answer += "{0:02x}".format(ord(byte_list[i])).upper()
        if (i != len(byte_list) - 1):
            answer += " "
        i += 1
    return(answer)

# Driver EPICS para as fontes

class PSDriver(Driver):

    # Construtor da classe

    def __init__(self):

        # Chama o construtor da superclasse

        Driver.__init__(self)

        # Inicializa a interface serial

        self.serial_init()

        # Rotina de inicialização para o controlador das fontes

        for ps_name in power_supplies.keys():

            ps_address = power_supplies[ps_name]

            # Limpa os grupos de variáveis BSMP

            self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x32", "\x00", "\x00"]), 100.0)
            answer = self.serial_read()

            # Criação de grupo de variáveis BSMP que serão lidas a 10 Hz

            self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x30", "\x00", "\x06", "\x00", "\x01", "\x02", "\x19", "\x1A", "\x1B"]), 100.0)
            answer = self.serial_read()

            # Reseta os interlocks da fonte

            self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x01", "\x06"]), 100.0)
            answer = self.serial_read()

            time.sleep(0.1)

            # Liga a fonte e fecha a sua malha de controle

            self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x01", "\x00"]), 100.0)
            answer = self.serial_read()

            time.sleep(0.3)

            self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x01", "\x03"]), 100.0)
            answer = self.serial_read()

            # Zera a corrente de saída da fonte

            self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x05", "\x10"] + PSDriver._list(struct.pack("<f", 0.0))), 100.0)
            answer = self.serial_read()

            # Espera 1 s

            time.sleep(1)

        # Define condições iniciais de algumas variáveis EPICS

        self.setParamStatus("SerialNetwork" + str(CRATE) + ":Sync", Alarm.NO_ALARM, Severity.NO_ALARM)
        self.setParamStatus("SerialNetwork" + str(CRATE) + ":Count", Alarm.NO_ALARM, Severity.NO_ALARM)

        for ps_name in power_supplies.keys():
            self.setParamStatus(ps_name + ":Current-SP", Alarm.NO_ALARM, Severity.NO_ALARM)
            self.setParamStatus(ps_name + ":IntlkLabels-Cte", Alarm.NO_ALARM, Severity.NO_ALARM)
            self.setParamStatus(ps_name + ":OpMode-Sel", Alarm.NO_ALARM, Severity.NO_ALARM)
            self.setParamStatus(ps_name + ":OpMode-Sts", Alarm.NO_ALARM, Severity.NO_ALARM)
            self.setParamStatus(ps_name + ":Reset-Cmd", Alarm.NO_ALARM, Severity.NO_ALARM)
            self.setParamStatus(ps_name + ":WfmData-SP", Alarm.NO_ALARM, Severity.NO_ALARM)

        # Fila de prioridade com as operações a serem realizadas no hardware de mais baixo nível
        # (controlador da fonte). Operações de escrita no controlador possuem prioridade sobre as
        # operações de leitura.

        self.queue = Queue()

        # Objeto do tipo Event para temporização da leitura dos parâmetros do controlador

        self.event = threading.Event()

        # Cria, configura e inicializa as três threads auxiliares do programa

        self.process = threading.Thread(target = self.processThread)
        self.scan = threading.Thread(target = self.scanThread)

        self.process.setDaemon(True)
        self.scan.setDaemon(True)

        self.process.start()
        self.scan.start()

    # Thread que, periodicamente (dez vezes por segundo), enfileira operações de leitura dos
    # parâmetros do controlador da fonte.

    def scanThread(self):

        while (True):
            self._updatePV("SerialNetwork" + str(CRATE) + ":Count", PRUserial485_read_pulse_count_sync())
            for ps_name in power_supplies.keys():
                self.queue.put((1, ["PS_READ_PARAMETERS", power_supplies[ps_name]]))
            if (self.getParam("SerialNetwork" + str(CRATE) + ":Sync") == 0):
                self.event.wait(0.1)
            else:
                self.event.wait(1)

    # Thread que processa a fila de operações que devem ser efetuadas no controlador da fonte

    def processThread(self):

        # Laço que executa indefinidamente

        while (True):

            # Retira a próxima operação da fila

            item = self.queue.get(block = True)
            operation = item[1][0]
            if (sys.version_info[0] == 2):
                for (ps_name, ps_address) in power_supplies.iteritems():
                    if (ps_address == item[1][1]):
                        break
            else:
                for (ps_name, ps_address) in power_supplies.items():
                    if (ps_address == item[1][1]):
                        break

            # Verifica a operação a ser realizada

            if (operation == "PS_READ_PARAMETERS"):

                # Operação de leitura de parâmetros

                # Solicita os valores das variáveis do grupo BSMP de ID 3 (criado na inicialização
                # do programa).

                self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x12", "\x00", "\x01", "\x03"]), 10.0)
                answer = self.serial_read()

                if (len(answer) == 27):

                    if ((PSDriver.verifyChecksum(answer) == True) and (answer[0] == "\x00") and (answer[1] == "\x13") and (answer[2] == "\x00") and (answer[3] == "\x16")):

                        # Se o dispositivo respondeu adequadamente, atualiza os valores das
                        # variáveis EPICS associadas.

                        ps_status = ord(answer[4]) + (ord(answer[5]) << 8)
                        if (sys.version_info[0] == 2):
                            self._updatePV(ps_name + ":Current-RB", struct.unpack("<f", "".join(answer[6:10]))[0])
                            self._updatePV(ps_name + ":CurrentRef-Mon", struct.unpack("<f", "".join(answer[10:14]))[0])
                        else:
                            self._updatePV(ps_name + ":Current-RB", struct.unpack("<f", bytes([ord(element) for element in answer[6:10]]))[0])
                            self._updatePV(ps_name + ":CurrentRef-Mon", struct.unpack("<f", bytes([ord(element) for element in answer[10:14]]))[0])
                        ps_soft_interlocks = ord(answer[14]) + (ord(answer[15]) << 8) + (ord(answer[16]) << 16) + (ord(answer[17]) << 24)
                        ps_hard_interlocks = ord(answer[18]) + (ord(answer[19]) << 8) + (ord(answer[20]) << 16) + (ord(answer[21]) << 24)
                        if (sys.version_info[0] == 2):
                            self._updatePV(ps_name + ":Current-Mon", struct.unpack("<f", "".join(answer[22:26]))[0])
                        else:
                            self._updatePV(ps_name + ":Current-Mon", struct.unpack("<f", bytes([ord(element) for element in answer[22:26]]))[0])

                        intlk_mon_value = 0
                        intlk_mon_value += ps_soft_interlocks & (0b1 << 0) # "Overtemperature on module"
                        intlk_mon_value += ps_hard_interlocks & (0b1 << 0) # "Overcurrent on load"
                        intlk_mon_value += ps_hard_interlocks & (0b1 << 1) # "Overvoltage on load"
                        intlk_mon_value += ps_hard_interlocks & (0b1 << 2) # "Overvoltage on DC-Link"
                        intlk_mon_value += ps_hard_interlocks & (0b1 << 3) # "Undervoltage on DC-Link"
                        intlk_mon_value += ps_hard_interlocks & (0b1 << 4) # "DC-Link input relay fail"
                        intlk_mon_value += ps_hard_interlocks & (0b1 << 5) # "DC-Link input fuse fail"
                        intlk_mon_value += ps_hard_interlocks & (0b1 << 6) # "Fail on module drivers"
                        self._updatePV(ps_name + ":Intlk-Mon", intlk_mon_value)

                        state = ps_status & 0b1111
                        if (state <= 2):
                            self._updatePV(ps_name + ":OpMode-Sts", state)
                        elif (state == 3):
                            if (new_op_modes[ps_name] != None):
                                self._updatePV(ps_name + ":OpMode-Sts", new_op_modes[ps_name])
                                new_op_modes[ps_name] = None

                        continue

                if (len(answer) == 0):

                    # Se o dispositivo não respondeu, seta o alarme de todas as variáveis EPICS como
                    # INVALID TIMEOUT.

                    update_flag = 0
                    pv_names = []
                    for suffix in pv_suffixes:
                        pv_names.append(ps_name + suffix)
                    for pv_name in pv_names:
                        if ((self.pvDB[pv_name].alarm != Alarm.TIMEOUT_ALARM) or (self.pvDB[pv_name].severity != Severity.INVALID_ALARM)):
                            self.setParamStatus(pv_name, Alarm.TIMEOUT_ALARM, Severity.INVALID_ALARM)
                            update_flag = 1
                    if (update_flag == 1):
                        self.updatePVs()

                else:

                    # Se o dispositivo respondeu, mas não de forma correta, seta o alarme de todas
                    # as variáveis EPICS como INVALID READ.

                    update_flag = 0
                    pv_names = []
                    for suffix in pv_suffixes:
                        pv_names.append(ps_name + suffix)
                    for pv_name in pv_names:
                        if ((self.pvDB[pv_name].alarm != Alarm.READ_ALARM) or (self.pvDB[pv_name].severity != Severity.INVALID_ALARM)):
                            self.setParamStatus(pv_name, Alarm.READ_ALARM, Severity.INVALID_ALARM)
                            update_flag = 1
                    if (update_flag == 1):
                        self.updatePVs()

                    # Se a execução chegou até aqui, muito provavelmente o controlador da fonte
                    # passou por um ciclo de alimentação. É necessário então reiniciar o IOC para
                    # que a rotina de inicialização do controlador seja novamente executada.

            elif (operation == "PS_TURN_ON"):

                # Liga a fonte e fecha a sua malha de controle

                self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x01", "\x00"]), 100.0)
                answer = self.serial_read()

                time.sleep(0.3)

                self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x01", "\x03"]), 100.0)
                answer = self.serial_read()

            elif (operation == "PS_TURN_OFF"):

                # Desliga a fonte

                self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x01", "\x01"]), 100.0)
                answer = self.serial_read()

                time.sleep(0.3)

            elif (operation == "PS_SET_OUTPUT_CURRENT"):

                # Seta uma nova corrente de saída na fonte

                self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x05", "\x10"] + PSDriver._list(struct.pack("<f", item[1][2]))), 100.0)
                answer = self.serial_read()

            elif (operation == "PS_RESET_INTERLOCKS"):

                # Reseta os interlocks da fonte

                self.serial_write(PSDriver.includeChecksum([chr(ps_address), "\x50", "\x00", "\x01", "\x06"]), 100.0)
                answer = self.serial_read()

                time.sleep(0.1)

            elif (operation == "PS_SET_RAMP_CURVE"):

                curves[ps_address] = self.getParam(ps_name + ":WfmData-SP")

                sorted_addresses = sorted(curves.keys())

                if (len(sorted_addresses) == 1):
                    PRUserial485_curve(curves[sorted_addresses[0]], [0.0] * len(curves[sorted_addresses[0]]), [0.0] * len(curves[sorted_addresses[0]]), [0.0] * len(curves[sorted_addresses[0]]))
                elif (len(sorted_addresses) == 2):
                    PRUserial485_curve(curves[sorted_addresses[0]], curves[sorted_addresses[1]], [0.0] * len(curves[sorted_addresses[0]]), [0.0] * len(curves[sorted_addresses[0]]))
                elif (len(sorted_addresses) == 3):
                    PRUserial485_curve(curves[sorted_addresses[0]], curves[sorted_addresses[1]], curves[sorted_addresses[2]], [0.0] * len(curves[sorted_addresses[0]]))
                else:
                    PRUserial485_curve(curves[sorted_addresses[0]], curves[sorted_addresses[1]], curves[sorted_addresses[2]], curves[sorted_addresses[3]])

    # Método que seta um novo valor para uma variável EPICS

    def _updatePV(self, pv_name, new_value):
        update_flag = 0
        if (new_value != self.pvDB[pv_name].value):
            self.setParam(pv_name, new_value)
            update_flag = 1
        if (self.pvDB[pv_name].severity == Severity.INVALID_ALARM):
            self.setParamStatus(pv_name, Alarm.NO_ALARM, Severity.NO_ALARM)
            update_flag = 1
        if (update_flag == 1):
            self.updatePVs()

    # Escrita em PVs

    def write(self, reason, value):

        if (reason in PVs.keys()):

            ps_name = reason.split(":")[0] + ":" + reason.split(":")[1]

            if (reason == ps_name + ":Current-SP"):
                if (((value >= -10.0) and (value <= 10.0)) and (self.getParam(ps_name + ":OpMode-Sts") == 3)):
                    self.queue.put((0, ["PS_SET_OUTPUT_CURRENT", power_supplies[ps_name], value]))
                    self.setParam(reason, value)
                else:
                    return(False)
            elif (reason == ps_name + ":OpMode-Sel"):
                if ((value == 0) or (value == 3) or (value == 6)):
                    self.setParam(reason, value)
                    if (value == 0):
                        self.queue.put((0, ["PS_TURN_OFF", power_supplies[ps_name]]))
                    else:
                        self.queue.put((0, ["PS_TURN_ON", power_supplies[ps_name]]))
                        new_op_modes[ps_name] = value
                else:
                    return(False)
            elif (reason == ps_name + ":Reset-Cmd"):
                self.queue.put((0, ["PS_RESET_INTERLOCKS", power_supplies[ps_name]]))
                self.setParam(reason, self.getParam(ps_name + ":Reset-Cmd") + 1)
            elif (reason == ps_name + ":WfmData-SP"):
                if (len(value) <= 4000):
                    self.setParam(reason, value)
                    self.queue.put((0, ["PS_SET_RAMP_CURVE", power_supplies[ps_name]]))
                else:
                    return(False)
            elif (reason == "SerialNetwork" + str(CRATE) + ":Sync"):
                self.setParam(reason, value)
                if (value == 0):
                    PRUserial485_sync_stop()
                elif (value == 1):
                    PRUserial485_sync_start(sorted(curves.keys())[0], 100)
                else:
                    return(False)
        else:
            return(False)

    # Inicializa a interface serial

    def serial_init(self):
        if (sys.version_info[0] == 2):
            PRUserial485_open(6, "M")
        else:
            PRUserial485_open(6, b"M")
        PRUserial485_sync_stop()
        PRUserial485_clear_pulse_count_sync()

    # Escreve mensagem na interface serial

    def serial_write(self, stream, timeout):
        PRUserial485_write(stream, timeout)

    # Lê mensagem da interface serial

    def serial_read(self):
        return(PRUserial485_read())

    # Método que inclui o byte de checksum a uma mensagem passada como argumento

    @staticmethod
    def includeChecksum(string):
        counter = 0
        i = 0
        while (i < len(string)):
            counter += ord(string[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        return(string + [chr(counter)])

    # Método que verifica o checksum de uma mensagem recebida

    @staticmethod
    def verifyChecksum(string):
        counter = 0
        i = 0
        while (i < len(string) - 1):
            counter += ord(string[i])
            i += 1
        counter = (counter & 0xFF)
        counter = (256 - counter) & 0xFF
        if (string[len(string) - 1] == chr(counter)):
            return(True)
        else:
            return(False)

    # Método criado para compatibilizar o código entre Python 2 e 3

    @staticmethod
    def _list(input):
        if (sys.version_info[0] == 2):
            return(list(input))
        else:
            return([chr(element) for element in input])

# Rotina executada quando o programa é lançado

if (__name__ == '__main__'):

    # Imprime uma mensagem inicial na tela

    sys.stdout.write("IOC.py\n")
    sys.stdout.write(time_string() + "Programa inicializado.\n")
    sys.stdout.flush()

    # Inicializa o servidor EPICS com as PVs das fontes

    CAserver = SimpleServer()
    CAserver.createPV("", PVs)
    driver = PSDriver()

    # Laço que executa indefinidamente

    while (True):
        CAserver.process(0.1)
