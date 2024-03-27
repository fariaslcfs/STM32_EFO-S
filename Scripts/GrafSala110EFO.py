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
from matplotlib import pyplot as plt
from matplotlib import animation
from PyQt5 import QtGui

'''------ Teste de conexão -------'''
MessageBox = ctypes.windll.user32.MessageBoxW
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
    MessageBox(None, 'Verifique sua conexão', 'Atenção', 0)
'''--------------------------------------------------------'''

tempoAtualizacao = int(input("Insira o tempo de atualização do gráfico em segundos: ")) * 1000

# fAlarme = open("tempAlarme.txt", "r")
# tAlarme = int(fAlarme.read())
# fAlarme.close()

fig, ax  = plt.subplots(2, num=None, figsize=(6.8, 4.8), dpi=100, facecolor='w', edgecolor='k')
plt.rcParams['toolbar'] = 'None'
fig.tight_layout(pad=6)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

path_icon = os.path.dirname(__file__) + './pictures/lof-mh.ico'
man = plt.get_current_fig_manager()
man.window.setWindowIcon(QtGui.QIcon(path_icon))

leituras = 10
tempoLeitura = 30
strTAtualizacao = str("%d" %(tempoAtualizacao/1000))
### TEMPERATURE DE ALARME NO GRÁFICO ###
tAlarme = 30
src = r"sensorTempHum.log"

def animar(i):
    try:
        with open(src) as f:
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
            acAlarm = linha[-2:]
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
        #tabgraf2 = ''
        for i in y[-leituras:]:
            #tabgraf2 = tabgraf2 + str(i) + ' °C    '
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

        wtitle = 'EFO - SALA 100 -- Temperatura de Alarme: ' + str(tAlarme) + " °C -- Intervalo de Atualização: " + strTAtualizacao + " s"
        man.set_window_title(wtitle)
        #fig.canvas.set_window_title(wtitle)
         
        ax[0].clear()
        ax[1].clear()
            
        textstr = str(yi) + " °C"
        ax[1].text(0.15, 1.60, "Atual: " + textstr, transform=ax[1].transAxes, fontsize=12, verticalalignment='top', color='red', bbox=dict(facecolor='none', edgecolor='none'))

        textstr = str(mdpartial) + " °C"
        ax[1].text(0.58, 1.60, "Média: " + textstr, transform=ax[1].transAxes, fontsize=12, verticalalignment='top', color='blue', bbox=dict(facecolor='none', edgecolor='none'))

        if (yi >= tAlarme):
            textstr = str(yi) + " °C - Temperatura excessiva na sala 110 EFO-S!"
            ax[0].text(0.05, 0.95, textstr, transform=ax[0].transAxes, fontsize=10, verticalalignment='top', bbox=props)
            ax[1].text(0.05, 0.95, textstr, transform=ax[1].transAxes, fontsize=10, verticalalignment='top', bbox=props)
			
        ax[0].plot(x,y,'r--', linewidth=0.8)
        ax[0].plot(x,ymd,'b',linewidth=1.0)
        #ax[0].text(0.40, 0.93, "T atual: " + str(yi)+" °C", transform=ax[0].transAxes, fontsize=8, verticalalignment='top', bbox=props)
        ax[1].plot(xpartial, ypartial, 'r--', linewidth=0.9, marker='.')
        ax[1].plot(xpartial, ymdpartial, 'b', linewidth=1.0)
        #ax[1].text(0.40, 0.93, "T atual: " + str(yi)+" °C", transform=ax[1].transAxes, fontsize=8, verticalalignment='top', bbox=props)
        #plt.gcf().text(0.16, 0.05, tabgraf2, fontsize=9)
        #plt.text(0.16, 0.05, tabgraf2, fontsize=9, transform=plt.gcf().transFigure)
        
        t = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        txt1 = 'Tamanho do log: ' + sizeFile + " " + percentFile + ' - Dias gravados: ' + str(dias) + '\n[' + t + ']\n\nTemperatura °C'
        txt2 = 'Temperatura °C - Dados de ' + str("%d"%(leituras/2)) + ' minuto(s)'

        ax[0].set_title(txt1, loc='center', pad=0.1)
        ax[1].set_title(txt2, loc='center', pad=0.1)
        txt3 = 'leituras (30 em 30s)'
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
        ax[0].grid(True)
        ax[1].grid(True)

    except:
        time.sleep(random.randint(5,10))

animar(0)
ani = animation.FuncAnimation(fig, animar, interval = tempoAtualizacao)
plt.show()