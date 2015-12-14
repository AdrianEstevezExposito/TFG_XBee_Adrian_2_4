#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import sys
import os
import time
import threading
import Queue
import re
import readline
from Conexiones import *
from DialogaAPI2 import *
    
class T_pulsador(threading.Thread): 
  # Se indica que es una clase heredada de Thread que fue importada por threading.
  dic_pulsadores =  {"1":"","2":"","3":"","4":"","5":"","6":"","7":"DIO11","8":"","9":"","10":"","11":"DIO4","12":"GPIO7","13":"","14":"","15":"DIO5","16":"","17":"DIO3","18":"DIO2","19":"DIO1","20":"DIO0"}
  
  def __init__(self, q, q_boton, stop, pin):
    threading.Thread.__init__(self)	# Importante, sin esto no funciona
    self.in_queue = q
    self.in_boton = q_boton		# Mensaje que llega desde dialogaAPI
    self.detener_hilo = stop
    self.pin_boton = pin
    self.empieza = 0.0
    self.doble_pulsacion = False
  
  def opciones(self):
    
    
  def run(self): # Contiene el codigo a ejecutar por el hilo.
    while self.detener_hilo.empty() == True:
      if self.in_boton.empty() == False:
	valor = self.in_boton.get()
	comando = self.dic_pulsadores[self.pin_boton]
	comando_on = comando
	comando_off= comando
	comando_on += "=0"
	comando_off += "=1"
	comando += ".*"
	m = re.search(comando, valor)
	if m:
	  #print "Se ha pulsado el botón y se ha devuelto {}".format(m.group(0))
	  m_0 = re.search(comando_on, m.group(0))
	  m_1 = re.search(comando_off, m.group(0))
	  if m_0:
	    print "---Pulsado--- -> {}".format(m_0.group(0))
	    self.empieza = time.time()
	    empieza_int = float(self.empieza)
	  if m_1:
	    print "---Soltado--- -> {}".format(m_1.group(0))
	    elapsed = time.time() - self.empieza
	    print "Tiempo de pulsación: {}".format(elapsed)
	    #self.in_queue.put("E13:P24")
	    if elapsed < 2.0:
	      time.sleep(1)
	      if self.in_boton.empty() == False:
		print "--Pulsación Doble--"
		self.doble_pulsacion = True
	      else:
		if self.doble_pulsacion == True:
		  self.doble_pulsacion = False
		else:
		  print "--Pulsación Simple--"
	    elif elapsed < 5.0:
	      print "--Pulsación Larga--"
	    elif elapsed > 5.0:
	      print "--Pulsación Muy Larga--"
	else:
	  print "ERROR al pulsar el botón. Se ha devuleto {}".format(valor)

class T_indicador(threading.Thread): 
  # Se indica que es una clase heredada de Thread que fue importada por threading.
  def __init__(self, q, q_indicador, com_M_on, com_M_off, opt):
    threading.Thread.__init__(self)	# Importante, sin esto no funciona
    self.n = 0
    self.in_queue = q
    self.detener_apagado = q_indicador
    self.comando_on = com_M_on
    self.comando_off = com_M_off
    self.blink_or_sleep = opt
    
  def run(self): # Contiene el codigo a ejecutar por el hilo.
    if self.blink_or_sleep == "2":
      while True:
	self.in_queue.put(self.comando_on)
	print "\nEncendiendo indicador..."
	time.sleep(self.n)
	if self.detener_apagado.empty() == False:
	  print "\nOperación de apagado cancelada."
	  self.detener_apagado.queue.clear()
	  break
	self.in_queue.put(self.comando_off)
	print "\nTiempo esperando = {}".format(self.n)
	break
      
    elif self.blink_or_sleep == "3":
      while True:
	if self.detener_apagado.empty() == False:
	  print "\nOperación de parpadeo cancelada."
	  self.detener_apagado.queue.clear()
	  break	
	self.in_queue.put(self.comando_on)
	#print "\nEncendiendo indicador..."
	time.sleep(self.n)
	if self.detener_apagado.empty() == False:
	  print "\nOperación de parpadeo cancelada."
	  self.detener_apagado.queue.clear()
	  break
	self.in_queue.put(self.comando_off)
	#print "\nApagando Indicador..."
	time.sleep(self.n)

class modulo(threading.Thread):
   nombreModulo = ""
   archivoModulo = ""
   archivoPines = ""
   archivoDispositivos = ""
   
   dic_comandos =  {"1":"P0","2":"","3":"","4":"P2","5":"","6":"","7":"P1","8":"","9":"","10":"","11":"D4","12":"","13":"","14":"","15":"D5","16":"D6","17":"D3","18":"D2","19":"D1","20":"D0"}
   
   dic_com_default = {"1":"P01","2":"","3":"","4":"P24","5":"","6":"","7":"P14","8":"","9":"","10":"","11":"D40","12":"","13":"","14":"","15":"D51","16":"D60","17":"D30","18":"D22","19":"D10","20":"D03","Boton":"IC8bf"}
   
   
  # pinescargados = [] #Es posible que así esté mal instanciado
   
   
   def __init__(self):
     threading.Thread.__init__(self)  # Importante, sin esto no funciona, basta con un copy/paste.
     while True:
       try:
	 self.nombreModulo = raw_input("Nombre del módulo>")
       except EOFError: #EOF
	 print "--Saliendo del programa--"
	 sys.exit(1)
       if len(self.nombreModulo) == 0:
	   continue
       self.pinescargados = {}  # crea una nueva lista vacía para cada modulo
       self.dicpines_str = {}	# además de otra para la copia en formato str.
       
       self.dicdispositivos = {}	# diccionario en el que guardar el nombre de cada actuador
       self.dicpines_asignados = {}	# diccionario en el que guardar la asociacion nombre-pin
       
       self.com_M = ""
       self.pasa = 0
       self.q = Queue.Queue()
       self.q_T_Indicador = Queue.Queue()
       self.q_T_Boton = Queue.Queue()	#Cola creada para ser utilizada en la creación del hilo principal
       self.stop = True
       self.q_stop = Queue.Queue()
       break
     
   def cargar(self):
     self.archivoModulo = self.nombreModulo
     self.archivoModulo += ".json"
     print "Nombre del archivo json del que cargar la configuración: {}".format(self.archivoModulo)
     try:
       with open(self.archivoModulo) as f:
	 self.pinescargados = json.load(f)
     except IOError:
       print "ERROR: El módulo indicado no dispone de fichero de configuración, inicialícelo primero."
       sys.exit(1)
     #print "Pines cargados: {}".format(self.pinescargados)
     #Se muestran "u" que significan unicode, no tiene importancia. (CREO)
     #Aún así, se crea una copia en dicpines_str con el diccionario en formato str.
     
   def to_str(self, data):
     nuevodicpines = {}
     for key, value in data.iteritems():
       if isinstance(key, unicode):
	 key = str(key)
       if isinstance(value, unicode):
	 value = str(value)
       nuevodicpines[key] = value
     self.dicpines_str = nuevodicpines
     print "Pines cargados convertidos a str: {}".format(self.dicpines_str)
     return data
   
   def nombrar(self):
     for k, v in self.dicpines_str.iteritems():
       if v != "":
	 try:
	   nombreDisp = raw_input("En el pin {} hay un {}. Distinguir como:>".format(k, v))
	 except EOFError:
	   print "--Saliendo del programa--"
	   sys.exit(1)
	 else:
	   self.dicpines_asignados[nombreDisp] = k	#guardar el pin
	   self.dicdispositivos[nombreDisp] = v		#guardar el tipo de dispositivo
       else:
	 print "Pin {} no asignado".format(k)
     print "---Nombre y clase de cada dispositivo:---\n {}\n".format(self.dicdispositivos)
     
     #Crear el nombre de los archivos de configuración
     config_pines = self.nombreModulo
     config_pines += "_pines.json"
     config_disp = self.nombreModulo
     config_disp += "_dispositivos.json"
     
     with open(config_pines, 'w') as outfile:
      json.dump(self.dicpines_asignados, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
     with open(config_disp, 'w') as outfile:
      json.dump(self.dicdispositivos, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


   def check_config(self):
     
     #Crear el nombre de los archivos de configuración
     self.archivoPines = self.nombreModulo
     self.archivoPines += "_pines.json"
     self.archivoDispositivos = self.nombreModulo
     self.archivoDispositivos += "_dispositivos.json" 
     
     try:
       with open(self.archivoPines) as f:
	 self.dicpines_asignados = json.load(f)
     except IOError:
       print "No existe configuración de pines previa, se pedirá a continuacion"
       return True
     else:
       print "Configuración de pines cargada con éxito:\n {}\n".format(self.dicpines_asignados)
     
     try:
       with open(self.archivoDispositivos) as f:
	 self.dicdispositivos = json.load(f)
     except IOError:
       print "No existe configuración de dispositivos previa, se pedirá a continuacion"
       self.dicpines_asignados = {}
       return True
     else:
       print "Configuración de dispositivos cargada con éxito:\n {}\n".format(self.dicdispositivos)
       
     return False
   
   def conf_boton(self, nombre_b, opt_b):
     try:
       disp_b = raw_input("Nombre del dispositivo con el qu interactuará el botón>")
     except EOFError: #EOF
       self.stop = False
       self.q_stop.put("STOP")
       sys.exit(1)  
     if self.dicdispositivos.has_key(disp_b):
       tipo_disp_b = self.dicdispositivos[disp_b]
       #CONTINUAR AQUÍ CON EL ENLACE DE DICCIONARIOS (papel de la libreta)
     else:
       print "ERROR: El dispositivo indicado no existe\n"
     
     
   
   def run(self):
      try:
	def_manual = raw_input("¿Cargar configuración por defecto?\n(s/n)>")
      except EOFError: #EOF
	self.stop = False
	self.q_stop.put("STOP")
	sys.exit(1)  
      if def_manual == "s":
	print "Cargando configuración inicial por defecto."
	for key, value in self.dic_com_default.iteritems():
	  if value != "":
	    time.sleep(4)
	    s = self.nombreModulo
	    s += ":"
	    s += value
	    print "Comando enviado: {}".format(s)
	    self.q.put(s)
    
      readline.parse_and_bind('set editing-mode vi')
      
      self.q_stop.queue.clear()
      for k, v in self.dicpines_str.iteritems():
	if v == "Pulsador":
	  hilo_boton = T_pulsador(self.q, self.q_T_Boton, self.q_stop, k)
	  
	  hilo_boton.start()
      
      print "Introduzca -comando- para invocar un comando directamente\n"

      while True:
	
	time.sleep(1)
	
	self.pasa = 0
	#---#
	try:
	  interactuado = raw_input("Nombre del dispositivo con el que interactuar>")
	except EOFError:
	  self.stop = False
	  self.q_stop.put("STOP")
	  print "--Saliendo del programa--"
	  break
	if len(interactuado) == 0:
	  continue
	
	if interactuado == "comando":
	  try:
	    s = raw_input("Esperando comandos> ")
	  except EOFError: #EOF
	    self.stop = False
	    self.q_stop.put("STOP")
	    print "--Saliendo del programa--"
	    break
	  if len(s) == 0:
	    continue
	  self.q.put(s)
	  continue
	  
	if self.dicdispositivos.has_key(interactuado):
	  print "El dispositivo '{}' es un {}.\n".format(interactuado, self.dicdispositivos[interactuado])
	else:
	  print "El nombre de dispositivo indicado no existe, pruebe otra vez\n"
	  continue
	print "Para el dispositivo '{}' existen las siguientes acciones:".format(interactuado)
	tipo_actual = self.dicdispositivos[interactuado]
	self.dic_options[tipo_actual](self, interactuado)
	
	#---#
	if self.pasa == 0:
	  try:
	    c_manual = raw_input("¿Introducir el comando indicado?\n(s/n)>")
	  except EOFError: #EOF
	    self.stop = False
	    self.q_stop.put("STOP")
	    break    
	  if c_manual == "s":
	    s = self.com_M
	  else:
	    try:
	      s = raw_input("Esperando comandos> ")
	    except EOFError: #EOF
	      self.stop = False
	      self.q_stop.put("STOP")
	      break
	  if len(s) == 0:
	    continue
	  
	  self.q.put(s)
 
   
   def f_actuadores(self, nombre):
     while True:
      print "1-Activar actuador \n2-Activar actuador durante cierto tiempo \n3-Desactivar el actuador"
      try:
	opt = raw_input("Opción>")
      except EOFError:
	print "--Saliendo del programa--"
	self.stop = False
	self.q_stop.put("STOP")
	sys.exit(1)
      if len(opt) == 0:
	continue
      if opt == "1":
	print "Se activará actuador.\n"
      elif opt == "2":
	print "Se activará el actuador durante cierto tiempo\n"
      elif opt == "3":
	print "Se desactivará el actuador\n"
      else:
	print "Opción no válida. Opciones válidas: 1 -- 2 -- 3"
	continue
      print "El pin sobre el que se actuará será el {}\n".format(self.dicpines_asignados[nombre])
      pin_actual = self.dicpines_asignados[nombre]
      if self.dic_comandos[pin_actual] != "":
	self.com_M = self.nombreModulo
	self.com_M += ":"
	self.com_M += self.dic_comandos[pin_actual]
	print "Por tanto, el comando utilizado será '{}'\n".format(self.com_M)
      else:
	print "ERROR: No existe comando para trabajar sobre este pin"
	self.com_M = ""
      break
     
   def f_indicadores(self, nombre):
     pin_actual = self.dicpines_asignados[nombre]     
     opc_indicador = ""
     while True:
      print "1-Activar indicador \n2-Activar durante cierto tiempo \n3-Activar con un tipo de parpadeo (tiempo apagado-tiempo encendido) \n4-Desactivar"
      try:
	opt = raw_input("Opción>")
      except EOFError:
	print "--Saliendo del programa--"
	self.stop = False
	self.q_stop.put("STOP")
	sys.exit(1)
      if len(opt) == 0:
	continue
      if opt == "1":
	print "Se activará el indicador.\n"
	opc_indicador = "5"
      elif opt == "2":
	print "Se activará el indicador durante cierto tiempo\n"
	self.q_T_Indicador.queue.clear()
	opc_indicador_on = "5"
	opc_indicador_off = "4"
	try:
	  t_wait = raw_input("Indique en segundos el tiempo durante el que activar el indicador>")
        except EOFError:
	  print "--Saliendo del programa--"
	  self.stop = False
	  self.q_stop.put("STOP")
	  sys.exit(1)
	com_M_on = self.nombreModulo
	com_M_on += ":"
	com_M_on += self.dic_comandos[pin_actual]
	com_M_off = com_M_on
	com_M_on += opc_indicador_on
	com_M_off += opc_indicador_off
	hilo_indicador = T_indicador(self.q, self.q_T_Indicador, com_M_on, com_M_off, opt)
	hilo_indicador.n = float(t_wait)
	hilo_indicador.start() # Se indica a la instancia de hilo que comience su ejecucion
	self.pasa = 1	# Pasa es un flag para no pedir comandos si se introduce esta opción (en ConsultaAPI3)
	break
      elif opt == "3":
	print "Parpadeo\n"
	self.q_T_Indicador.queue.clear()
	opc_indicador_on = "5"
	opc_indicador_off = "4"
	try:
	  t_wait = raw_input("Indique en segundos el intervalo de parpadeo del indicador>")
        except EOFError:
	  print "--Saliendo del programa--"
	  self.stop = False
	  self.q_stop.put("STOP")
	  sys.exit(1)
	com_M_on = self.nombreModulo
	com_M_on += ":"
	com_M_on += self.dic_comandos[pin_actual]
	com_M_off = com_M_on
	com_M_on += opc_indicador_on
	com_M_off += opc_indicador_off
	hilo_indicador = T_indicador(self.q, self.q_T_Indicador, com_M_on, com_M_off, opt)
	hilo_indicador.n = float(t_wait)
	hilo_indicador.start() # Se indica a la instancia de hilo que comience su ejecucion
	self.pasa = 1	# Pasa es un flag para no pedir comandos si se introduce esta opción (en ConsultaAPI3)
	break
      elif opt == "4":
	print "Se desactivará el indicador\n"
	opc_indicador = "4"
      else:
	print "Opción no válida. Opciones válidas: 1 -- 2 -- 3 -- 4"
	continue
      print "El pin sobre el que se actuará será el {}\n".format(self.dicpines_asignados[nombre])
      if self.dic_comandos[pin_actual] != "":
	self.com_M = self.nombreModulo
	self.com_M += ":"
	self.com_M += self.dic_comandos[pin_actual]
	self.com_M += opc_indicador
	print "Por tanto, el comando utilizado será '{}'\n".format(self.com_M)
	self.pasa = 0
	self.q_T_Indicador.put("X")
	#if self.flag_hilo_exe == 1:
	  #self.T_Comandos.start() # Se indica a la instancia de hilo que comience su ejecucion
	  #self.flag_hilo_exe = 0
      else:
	print "ERROR: No existe comando para trabajar sobre este pin"
	self.com_M = ""
      break
    
   def f_pulsadores(self, nombre):
     while True:
      print "Defina que quiere hacer para: \n1-Evento pulsación simple \n2-Evento pulsación doble \n3-Evento pulsación larga \n4-Evento pulsación muy larga"
      try:
	opt = raw_input("Opción>")
      except EOFError:
	print "--Saliendo del programa--"
	self.stop = False
	self.q_stop.put("STOP")
	sys.exit(1)
      if len(opt) == 0:
	continue
      if opt == "1":
	print "Evento pulsación simple\n"		#Pedir variable (dispositivo)
	conf_boton(nombre, opt)
      elif opt == "2":
	print "Evento pulsación doble\n"		#Pedir variable (dispositivo)
	conf_boton(nombre, opt)
      elif opt == "3":
	print "Evento pulsación larga\n"		#Pedir variable (dispositivo)
	conf_boton(nombre, opt)
      elif opt == "4":
	print "Evento pulsación muy larga\n"		#Pedir variable (dispositivo)
	conf_boton(nombre, opt)
      else:
	print "Opción no válida. Opciones válidas: 1 -- 2 -- 3 -- 4" 
	continue
      print "El pin sobre el que se actuará será el {}\n".format(self.dicpines_asignados[nombre])
      pin_actual = self.dicpines_asignados[nombre]
      if self.dic_comandos[pin_actual] != "":
	self.com_M = self.nombreModulo
	self.com_M += ":"
	self.com_M += self.dic_comandos[pin_actual]
	print "Por tanto, el comando utilizado será '{}'\n".format(self.com_M)
      else:
	print "ERROR: No existe comando para trabajar sobre este pin"
	self.com_M = ""	
      break
    
   def f_analogicos(self, nombre):
     while True:
      print "1-Fijar umbrales mínimo y máximo \n2-Fijar histéresis \n3-Evento zona mínima \n4-Evento zona máxima \n5-Evento zona media"
      try:
	opt = raw_input("Opción>")
      except EOFError:
	print "--Saliendo del programa--"
	self.stop = False
	self.q_stop.put("STOP")
	sys.exit(1)
      if len(opt) == 0:
	continue
      if opt == "1":
	print "Se fijarán los umbrales.\n"	#Pedir variable (valor actual potenciometro)
      elif opt == "2":
	print "Se fijará la histéresis\n"	#Pedir variable (valor actual potenciometro)
      elif opt == "3":
	print "Se definirá el evento de zona minima\n"	#Pedir variable (dispositivo)
      elif opt == "4":
	print "Se definirá el evento de zona maxima\n"	#Pedir variable (dispositivo) 
      elif opt == "5":
	print "Se definirá el evento de zona media\n"	#Pedir variable (dispositivo)
      else:
	print "Opción no válida. Opciones válidas: 1 -- 2 -- 3 -- 4 -- 5"
	continue
      print "El pin sobre el que se actuará será el {}\n".format(self.dicpines_asignados[nombre])
      pin_actual = self.dicpines_asignados[nombre]
      if self.dic_comandos[pin_actual] != "":
	self.com_M = self.nombreModulo
	self.com_M += ":"
	self.com_M += self.dic_comandos[pin_actual]
	print "Por tanto, el comando utilizado será '{}'\n".format(self.com_M)
      else:
	print "ERROR: No existe comando para trabajar sobre este pin"
	self.com_M = ""
      break
    
   # Mapear las opciones con su bloque de funcion
   dic_options = {"Actuador" : f_actuadores,
           "Indicador" : f_indicadores,
           "Pulsador" : f_pulsadores,
           "Analogico" : f_analogicos
   }

####################################################################
## Programa principal
if __name__ == "__main__":
  device = modulo()
  
  device.cargar()
  
  device.to_str(device.pinescargados)	#Necesario convertir los valores en string para mejor manejo
  
  if device.check_config():
    device.nombrar()

  while True:
    try:
      interactuado = raw_input("Nombre del dispositivo con el que interactuar>")
    except EOFError:
      print "--Saliendo del programa--"
      sys.exit(1)
    if len(interactuado) == 0:
      continue
    
    if device.dicdispositivos.has_key(interactuado):
      print "El dispositivo '{}' es un {}.\n".format(interactuado, device.dicdispositivos[interactuado])
    else:
      print "El nombre de dispositivo indicado no existe, pruebe otra vez\n"
      continue
    print "Para el dispositivo '{}' existen las siguientes acciones:".format(interactuado)
    tipo_actual = device.dicdispositivos[interactuado]
    device.dic_options[tipo_actual](device, interactuado)
    try:
      com = raw_input("Comando a enviar>")
    except EOFError:
      print "--Saliendo del programa--"
      sys.exit(1)
    if len(com) == 0:
      continue
    
    #SIGUIENTE: Comandos de botón. Investigar cómo cambiar dispositivo a interactuar segun tipo de pulsacion.
