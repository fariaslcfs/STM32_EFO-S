import os
import math
import time
import datetime
import random
import socket
import ctypes
import tkinter as tk
import matplotlib
import numpy as np
import serial, keyboard, smtplib
from shutil import copyfile
from tkinter import simpledialog
from matplotlib import pyplot as plt
from matplotlib import animation
from PyQt5 import QtGui

#from scriptSerial import scSerial


#Se for usar dois scripts#
#import scriptSerial as scSerial

########## Teste de conexão #########################
mBox = ctypes.windll.user32.MessageBoxW
confiaveis = ['1.1.1.1', '4.4.4.4', '8.8.8.8']
def check_host():
   global confiaveis
   for host in confiaveis:
     a=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     a.settimeout(.5)
     try:
       b=a.connect_ex((host, 80))
       if b==0: #ok, conectado
         return True
     except:
       pass
     a.close()
   return False

if not check_host():
    mBox(None, 'Verifique sua conexão', 'Atenção', 0)
#####################################################

######## Para usar caixa de texto ao invés de prompt de comando ########
#ROOT = tk.Tk()
#ROOT.withdraw()
#tAlarme = simpledialog.askstring(title="T de Alarme", prompt="Insira a temperatura de alarme (C)")
#tempoAtualizacao = simpledialog(title="Intervalo de atualização do gráfico", prompt="Insira o tempo em segundos")
########################################################################

########################### Globais ##############################
tAlarme = int(input("Insira a temperatura de alarme (C): "))
tempoAtualizacao = int(input("Insira o tempo de atualização do gráfico em segundos: ")) * 1000

strTAtualizacao = str("%d" %(tempoAtualizacao/1000))
leituras = 10
tempoLeitura = 30
src = "sensorTempHum.log"
#################################################################


############## Serial ##############
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

############# Fig, graf ############
fig, ax  = plt.subplots(2, num=None, figsize=(6.8, 4.8), dpi=100, facecolor='w', edgecolor='k')
plt.rcParams['toolbar'] = 'None'
fig.tight_layout(pad=6)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
man = plt.get_current_fig_manager()
path_icon = os.path.dirname(__file__) + './pictures/lof-mh.ico'
man.window.setWindowIcon(QtGui.QIcon(path_icon))
####################################

def animar(i):
    try:
        #sct(tAlarme)
        with open("sensorTempHum.log", "r") as f:
            dados = f.read()
        f.close()
  
        x = []
        xpartial = []
        y = []
        ypartial = []
	 
        aux = 1
        for linha in dados.split('\n'):
            if len(linha) == 0:
                continue
            xi = aux				
            aux += 1
            yi = int(linha[:2])
            x.append(xi)
            y.append(yi)
			
        # Média e offset para correto posicionamento das curvas
        mi = np.min(y)
        ma = np.max(y)
        offs = abs((ma - mi) / 2)
        lb = mi - offs
        ub = ma + offs
        md = np.mean(y)
        ymd = []
        for n in range(1,len(x)+1):
            ymd.append(md)
			
        dias = str('%.1f' %(((aux - 1) * tempoLeitura) / (3600 * 24)))            
		
        aux = 1
        tabgraf2 = ''
        for i in y[-leituras:]:
            tabgraf2 = tabgraf2 + str(i) + ' °C    '
            ypartial.append(i)
            xpartial.append(aux)
            aux += 1

        # Média e offset para correto posicionamento das curvas
        mipartial = np.min(ypartial)
        mapartial = np.max(ypartial)
        offspartial = abs((mapartial - mipartial) / 2)
        lbpartial = mipartial - offspartial
        ubpartial = mapartial + offspartial
        mdpartial = np.mean(ypartial)
        ymdpartial = []
		

        for n in range(1,len(xpartial)+1):
            ymdpartial.append(mdpartial)			
			
        fsize = int(os.stat(src).st_size)            
        percentFile = "(%.1f"%(fsize / 2097152 * 100) + "% de 2MB)"
        if fsize < 1024:
            sizeFile = str(fsize) + " B"			
        elif fsize >= 1024 and fsize < 1048576:
            sizeFile = "%.1f" %(fsize / 1024) + " KB"
        else:
            sizeFile = "%.1f" %(fsize / 1048576) + " MB"
        
        wtitle = 'FORNINHO -- Temperatura de Alarme: ' + str(tAlarme) + " || Atualização: " + strTAtualizacao + " s"
        #fig.canvas.set_window_title(wtitle)
        man.set_window_title(wtitle)
        
        ax[0].clear()
        ax[1].clear()
            
        if yi >= tAlarme:
            textstr = str(yi) + " °C - Temperatura excessiva no Forninho!"
            ax[0].text(0.05, 0.95, textstr, transform=ax[0].transAxes, fontsize=10, verticalalignment='top', bbox=props)
            ax[1].text(0.05, 0.95, textstr, transform=ax[1].transAxes, fontsize=10, verticalalignment='top', bbox=props)
			

        ax[0].plot(x,y,'r--', x, ymd, 'b', linewidth=0.8)
        #ax[0].text(0.40, 0.93, "T atual: " + str(yi)+" °C", transform=ax[0].transAxes, fontsize=8, verticalalignment='top', bbox=props)
        ax[1].plot(xpartial, ypartial, 'r--', xpartial, ymdpartial, 'b', linewidth=0.8)
        #ax[1].text(0.40, 0.93, "T atual: " + str(yi)+" °C", transform=ax[1].transAxes, fontsize=8, verticalalignment='top', bbox=props)
        #plt.text(0.16, 0.05, tabgraf2, fontsize=9, transform=plt.gcf().transFigure)
        
        t = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        txt1 = 'Tamanho do log: ' + sizeFile + " " + percentFile + ' - Dias gravados: ' + str(dias) + '\n[' + t + ']\n\nTemperatura Forninho °C'
        txt2 = 'Temperatura °C - Dados de ' + str("%d"%(leituras/2)) + ' minuto(s)'
        ax[0].grid(True)
        ax[1].grid(True)
        ax[0].set_title(txt1, loc='center', pad=0.1)
        ax[1].set_title(txt2, loc='center', pad=0.1)
        txt3 = '30 em 30s'
        ax[0].set_xlabel(txt3)
        ax[1].set_xlabel(txt3)
        ax[0].set_ylabel('Temp °C')
        ax[1].set_ylabel('Temp °C')
        ax[0].set_xlim([1,len(x)])
        ax[1].set_xlim([1,len(xpartial)])
        ax[0].set_ylim([lb, ub]) 
        ax[1].set_ylim([lbpartial, ubpartial]) 
        ax[0].legend(['Atual', 'Média'], fontsize=7)
        ax[1].legend(['Atual', 'Média'], fontsize=7)

    except:
        time.sleep(random.randint(15,30))

def sct(ta):
    txt = rl.readline().decode('utf-8').rstrip() 
    f = open(src, "a", buffering=256)
    fsize = int(os.stat(src).st_size)
    if fsize > 2097152:   # Se arquivo > 2MB renomeia e salva atual e começa outro do zero
        f.close()
        dst = "sensorTempHum" + "_" + datetime.now().strftime("%d%m%Y_%H%M%S") + '.log'
        os.copyfile(src, dst)
        f = open(src, "a", buffering=256)
    f.write(txt+'\n')
    f.flush()
    f.close()
    
    temp = int(txt[:2])
    if temp >= ta:
        msg = "Atenção!\nTemperatura (C) >= " + str(ta)
        mBox(None, msg, 'Atenção', 0)
        try:
            text = "ALARME DE TEMPERATURA NO FORNINHO\n\nTemperatura de alarme (C): "+str(ta)+"\nTemperatura atual (C): "+str(temp)+"\n\nLCCA EAH IEAv"
            email_text = 'Subject: {}\n\n{}'.format(subject,text)
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.ehlo()
            server.login(gmail_user, gmail_password)
            server.sendmail(sent_from, to, email_text)
            server.close()
            time.sleep(300)
        except:
            msg2 = 'Falha no envio de e-mail de alarme de temperatura'
            mBox(None, msg, 'Atenção', 0)     

animar(0)
ani = animation.FuncAnimation(fig, animar, interval = 5)
plt.show()
