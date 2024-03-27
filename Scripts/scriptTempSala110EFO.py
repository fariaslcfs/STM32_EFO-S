#Acaptado de: https://stackoverflow.com/questions/19908167/reading-serial-data-in-realtime-in-python

import os
import subprocess
import base64
import serial
import keyboard
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s  

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(256, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")    
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)


def enviaEmail(subject, userfrom, userto, p, svr, port, msg):
    email_text = 'Subject: {}\n\n{}'.format(subject, msg)
    server = smtplib.SMTP(svr, port)
    server.login(userfrom, p)
    server.sendmail(userfrom, userto, email_text)
    server.quit()
    print('###### E-MAIL ENVIADO ######')
    
###### Config Serial ######  
ser = serial.Serial('COM7', 19200)
rl = ReadLine(ser)
src = "sensorTempHum.log"

###### Config E-mail ######
dest1 = 'fariaslcfs@gmail.com'
dest2 = 'fariaslcfs@fab.mil.br'
code = 'U29taWwhZGV2NGM0Z29yZGENCg=='
zimbraFAB_server = 'smtp.fab.mil.br'
zimbraFAB_user = 'fariaslcfs@fab.mil.br'
port = 587
to = [dest1, dest2]
subject_temp = 'ALARME TEMPERATURA'
#subject_AC = 'ALARME ENERGIA AC'

tempAlarme = int(input("Digite a temperatura de alarme (°C): "))
numberOfReadings = int(input("Digite o número de leituras para envio de e-mail de alarme (1 leitura a cada 30 s): "))
print("\n")
count = 0
count2 = 0

while (not keyboard.is_pressed('q') or not keyboard.is_pressed('Q')):
    txt = rl.readline().decode('utf-8').rstrip()
    t = txt[:2]
    f = open(src, "a", buffering=587)
    fsize = int(os.stat(src).st_size)
    
    if fsize > 2097152:   # Se arquivo > 2MB renomeia, salva e começa outro do zero
        f.close()
        dst = "sensorTempHumAH08" + "_" + datetime.now().strftime("%d%m%Y_%H%M%S") + '.log'
        os.rename(src, dst)
        src = "sensorTempHum.log"
        f = open(src, "a", buffering=256)
    
    f.write(txt+'\n')
    f.flush()
    f.close()
    print(txt)
   
    temp = int(t)
    if temp >= tempAlarme:
        print(str(count+1) + " - Temperatura na sala 110 EFO-S >= " + str(tempAlarme) + " °C")
        count += 1
        try:
            elapsed = int(30 * (numberOfReadings) / 60)
            text = "ALARME DE TEMPERATURA NA SALA 110 EFO-S\n\nHora do alarme: " + datetime.now().strftime("%H:%M:%S") + "\nTempo entre e-mails: ~" + str(elapsed) + " min" + "\nTemperatura de alarme (Celsius): " +str(tempAlarme) + "\nTemperatura atual (Celsius): "+str(temp) + "\n\nLCCA EAH IEAv\n"      
            if count == 1:
                #pass
                enviaEmail(subject_temp, zimbraFAB_user, to, base64.b64decode(code).decode('utf-8').strip(), zimbraFAB_server, port, text)
            if count == numberOfReadings:
                count = 0
        except:
            print('Falha no envio de e-mail de alarme de temperatura.')

'''
    if txt[-2:] == "ac":
        print(str(count+1) + " - Sem Energia AC no Forninho")
        count2 += 1
        try:
            elapsed = int(30 * (numberOfReadings) / 60)
            text = "ALARME DE ENERGIA AC NO FORNINHO\n\nHora do alarme: " + datetime.now().strftime("%H:%M:%S") + "\nTempo entre e-mails: ~" + str(elapsed) + " min" + "\n\nLCCA EAH IEAv\n"
            if count2 == 1:
                #pass
                enviaEmail(subject_AC, zimbraFAB_user, to, base64.b64decode(code).decode('ascii').strip(), zimbraFAB_server, port, text)
            if count2 == numberOfReadings:
                count2 = 0
        except:
            print('Falha no envio de e-mail de alarme de energia AC.')
'''