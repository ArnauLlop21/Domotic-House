#!/usr/bin/env python
# coding=utf-8

#project done by: 
# Arnau Llop Iglesias 
#Tarragona, Catalonia

# sha dimportar les següents llibreries pel
#correcte funcionament de l'estepper

import sys # importa unes system specific parameters and functions
import time
import RPi.GPIO as GPIO 
import threading 
import socket
import smtplib
import requests
import json
import os

GPIO.setmode(GPIO.BCM) #anomena els pins pel nom GPIO, no pel nombre

SOCKPATH = "/var/run/lirc/lircd"
sock = None

pin_gas = 13
GPIO.setup(pin_gas, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

StepPins = [17, 19, 27, 22] #array amb la menció dels pins

for pin in StepPins:
  print ("Setup pins")
  GPIO.setup(pin,GPIO.OUT)
  GPIO.output(pin, False)
 
GPIO.setup(5,GPIO.OUT)

global USUARI
global PASS
global DESTINATARI
global ASSUMPTE
global COS

USUARI = 'YouPutYourEMailHere'
PASS = 'YouPutYourPasswordHere'
DESTINATARI = 'provesTDRllop@gmail.com' 
ASSUMPTE = 'RPi3 des de la casa domòtica'
COS = "Alarma desactivada, has estat tu?"

# definir la seqüencia descrita al full tècnic del fabricant  
Seq = [[1,0,0,1],
	   [1,0,0,0],
	   [1,1,0,0],
	   [0,1,0,0],
	   [0,1,1,0],
	   [0,0,1,0],
	   [0,0,1,1],
	   [0,0,0,1]]  

StepCount = len(Seq)
#print ("Introdueix el sentit de gir")
#StepDir = int(input(""))          
StepDir = 1

if len(sys.argv)>1:
  WaitTime = int(sys.argv[1])/float(1000)
else:
  WaitTime = 10/float(1000)

#StepCounter = 0

#timeout = time.time() + 5 #5 segons de bucle


def correu_alarma():
	try:
		s = smtplib.SMTP('smtp.gmail.com',587)
		
		s.ehlo()
		s.starttls()
		s.ehlo()
		
		s.login(USUARI, PASS)
		s.sendmail(USUARI, DESTINATARI, COS)
		s.quit()
		
		print 'Mail enviat!'
		
	except:
		
		print 'Quelcom ha fallat'

def notificacio_alarma():
	
	global api_key, notification_title, notification_message, url, data
	api_key = 'MSOHFBOD9Q83D8B5J8CWDAMND'
	notification_title = "Ull!!!"
	notification_message ="Alarma desactivada"
	url = "https://www.notifymydevice.com/push"
	data = {"ApiKey": api_key, "PushTitle":notification_title
	, "PushText": notification_message}

	headers = {'Content-Type': 'application/json'}
	
	global r
	
	r = requests.post(url, data=json.dumps(data), headers = headers)

	if r.status_code == 200:
		print 'Notification sent'
	else:
		print 'Something went wrong'

def pujada():
				timeout = time.time() + 15 #15 segons de bucle
				StepDir = -1
				test = 0
				StepCounter = 0
				trenca = False
				while not trenca:
					
					print StepCounter
					print Seq[StepCounter]
				
					for pin in range (0,4):
						xpin = StepPins[pin]
						if Seq[StepCounter][pin]!=0:
							GPIO.output (xpin,True)
						else:
							GPIO.output(xpin,False)
					
					StepCounter += StepDir
				
					if StepCounter>=StepCount:
						StepCounter = 0
				
					if StepCounter<0:
						StepCounter = StepCount + StepDir
				
					if test == 5 or time.time() > timeout:
						trenca = True
					test = test - 1	
					time.sleep(WaitTime)


def baixada():
				timeout = time.time() + 15 #15 segons de bucle
				StepDir = 1
				test = 0
				StepCounter = 0
				trenca = False
				while not trenca:
					
					print StepCounter
					print Seq[StepCounter]
				
					for pin in range (0,4):
						xpin = StepPins[pin]
						if Seq[StepCounter][pin]!=0:
							GPIO.output (xpin,True)
						else:
							GPIO.output(xpin,False)
					
					StepCounter += StepDir
				
					if StepCounter>=StepCount:
						StepCounter = 0
				
					if StepCounter<0:
						StepCounter = StepCount + StepDir
				
					if test == 5 or time.time() > timeout:
						trenca = True
					test = test - 1	
					time.sleep(WaitTime)

def init_irw():
	global sock
	sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
	print ('Starting up on %s' % SOCKPATH)
	sock.connect(SOCKPATH)

init_irw()

def next_key():
	'''Get the next key pressed. Return keyname,updown.
	'''
	while True:
		data = sock.recv (128)
		data = data.strip()
		
		if data:
			break
	
	words = data.split()
	return words[2], words[1]


def infiniteloopIR():
	global val
	val = 1
	GPIO.output(5,True)

	while True:
		keyname, updown = next_key()
		print next_key()
		print('%s (%s)' % (keyname, updown))
		time.sleep(1)
		
		if keyname == 'KEY_POWER' and val != 1:
			val = 1
			GPIO.output(5,True)
			correu_alarma()
			notificacio_alarma()

		elif keyname != 'KEY_POWER' and val != 0:
			val = 0
			GPIO.output(5,False)


def BucleInfinit():
	mpin=26
	tpin=25
	cap=0.000001
	adj=2.130620985
	i=0
	t=0
	while True:
	
		if val == 1:

			GPIO.setup(mpin, GPIO.OUT)
			GPIO.setup(tpin, GPIO.OUT)
			GPIO.output(mpin, False)
			GPIO.output(tpin, False)
			time.sleep(0.2)
			GPIO.setup(mpin, GPIO.IN)
			time.sleep(0.2)
			GPIO.output(tpin, True)
			starttime=time.time()
			endtime=time.time()
			
			while (GPIO.input(mpin) == GPIO.LOW):
				endtime=time.time()
				
				
			measureresistance=endtime-starttime
			res=(measureresistance/cap)*adj
			i=i+1
			t=t+res
			if i==10:
			
					t=t/i
					print(t)
					if t > 4000:
						pujada()
						time.sleep(5)
						baixada()
						time.sleep(5)
					#i=0
					#t=0
					i=0
					t=0
def infinit_gas():
	GPIO.setup(pin_gas, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


	while True:

		#print GPIO.input(pin_gas)

		if GPIO.input (pin_gas)  == 0:
			os.system("omxplayer -b /home/pi/Desktop/TDR/TDR_proves/OS_sound/so_alarma.wav")
		

		#else:
			#print("No gas")

thread1 = threading.Thread(target=infiniteloopIR)
thread1.start()

thread2 = threading.Thread(target=BucleInfinit)
thread2.start()

thread3 = threading.Thread(target=infinit_gas)
thread3.start()
