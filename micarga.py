#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import sys
import os
import time
import threading
import re
from Conexiones import *
from DialogaAPI import *


class T_indicador(threading.Thread): 
  # Se indica que es una clase heredada de Thread que fue importada por threading.
  def __init__(self):
    threading.Thread.__init__(self)  # Importante, sin esto no funciona, basta con un copy/paste.
    self.n = 0
    
  def run(self): # Contiene el codigo a ejecutar por el hilo.
    du2 = dialogoAPI( conexion_ser("/dev/ttyUSB0",115200) )
    du2.start()
    
    cmds = 'SH, SL, VR, AI, OP, CH, NI, ND'
    print "Enviando comandos AT locales '{}'".format(cmds)
    du2.comandosATlocal( cmds )

    print "Espere..."
    time.sleep(6)
    while True:
      print "\nEncendiendo indicador..."
      s = "E13:P05"
      m = re.search(r"([^:]*):(.*)", s)
      ( remota, comandos ) = m.groups()
      if len( remota )>0: #se epecifico nombre o dirección
	#Probamos primero con el nombre
	serial = du2.nombretoSerial( remota )
	if serial<0: #no se encontró nombre, tratamos dirección 16
	  serial = du2.dir16toSerial( hexStr2Int( remota ) )
	if serial<0:
	  print "Especificación remota '{}' no encontrada, NO enviamos".format( remota )
	  break
	Remoto = serial
	print "Usando dirección remota 0x{:X}".format( Remoto )
      if Remoto<0:
	print "No hay dirección remota válida almacenada, NO enviamos"
	break
      try:
	#print "Enviando comandos: >{}<".format(comandos)
	du2.comandosATremoto( Remoto, -1, comandos )
      except:
	print "Error al enviar comandos remotos '{}'".format( comandos )
	break
    
      time.sleep(self.n)
      
      s = "E13:P01"
      m = re.search(r"([^:]*):(.*)", s)
      ( remota, comandos ) = m.groups()
      if len( remota )>0: #se epecifico nombre o dirección
	#Probamos primero con el nombre
	serial = du2.nombretoSerial( remota )
	if serial<0: #no se encontró nombre, tratamos dirección 16
	  serial = du2.dir16toSerial( hexStr2Int( remota ) )
	if serial<0:
	  print "Especificación remota '{}' no encontrada, NO enviamos".format( remota )
	  break
	Remoto = serial
	print "Usando dirección remota 0x{:X}".format( Remoto )
      if Remoto<0:
	print "No hay dirección remota válida almacenada, NO enviamos"
	break
      try:
	#print "Enviando comandos: >{}<".format(comandos)
	du2.comandosATremoto( Remoto, -1, comandos )
      except:
	print "Error al enviar comandos remotos '{}'".format( comandos )
	
      print "\nApagando indicador. Tiempo encendido = {}".format(self.n)
      break
    du2.finish()
    du2.join()

class modulo:
   nombreModulo = ""
   archivoModulo = ""
   archivoPines = ""
   archivoDispositivos = ""
   
   dic_comandos =  {"1":"P0","2":"","3":"","4":"P2","5":"","6":"","7":"P1","8":"","9":"","10":"","11":"D4","12":"","13":"","14":"","15":"D5","16":"D6","17":"D3","18":"D2","19":"D1","20":"D0"}
   
   dic_com_default = {"1":"P01","2":"","3":"","4":"P20","5":"","6":"","7":"P10","8":"","9":"","10":"","11":"D40","12":"","13":"","14":"","15":"D51","16":"D60","17":"D30","18":"D22","19":"D10","20":"D01"}
  # pinescargados = [] #Es posible que así esté mal instanciado
   
   
   def __init__(self):
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
   
   def f_actuadores(self, nombre):
     while True:
      print "1-Activar actuador \n2-Activar actuador durante cierto tiempo \n3-Desactivar el actuador"
      try:
	opt = raw_input("Opción>")
      except EOFError:
	print "--Saliendo del programa--"
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
     opc_indicador = ""
     while True:
      print "1-Activar indicador \n2-Activar durante cierto tiempo \n3-Activar con un tipo de parpadeo (tiempo apagado/tiempo encendido) \n4-Desactivar"
      try:
	opt = raw_input("Opción>")
      except EOFError:
	print "--Saliendo del programa--"
	sys.exit(1)
      if len(opt) == 0:
	continue
      if opt == "1":
	print "Se activará el indicador.\n"
	opc_indicador = "5"
      elif opt == "2":
	print "Se activará el indicador durante cierto tiempo\n"
	try:
	  opt = raw_input("Indique en segundos el tiempo durante el que activar el indicador>")
        except EOFError:
	  print "--Saliendo del programa--"
	  sys.exit(1)
	hilo_indicador = T_indicador()
	hilo_indicador.n = float(opt)
	hilo_indicador.start() # Se indica a la instancia de hilo hilo que comience su ejecucion
	self.pasa = 1
	break
      elif opt == "3":
	print "Parpadeo\n"
	# Investigar función parpadeo.
      elif opt == "4":
	print "Se desactivará el indicador\n"
	opc_indicador = "4"
      else:
	print "Opción no válida. Opciones válidas: 1 -- 2 -- 3 -- 4"
	continue
      print "El pin sobre el que se actuará será el {}\n".format(self.dicpines_asignados[nombre])
      pin_actual = self.dicpines_asignados[nombre]
      if self.dic_comandos[pin_actual] != "":
	self.com_M = self.nombreModulo
	self.com_M += ":"
	self.com_M += self.dic_comandos[pin_actual]
	self.com_M += opc_indicador
	print "Por tanto, el comando utilizado será '{}'\n".format(self.com_M)
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
	sys.exit(1)
      if len(opt) == 0:
	continue
      if opt == "1":
	print "Evento pulsación simple\n"		#Pedir variable (dispositivo)
      elif opt == "2":
	print "Evento pulsación doble\n"		#Pedir variable (dispositivo)
      elif opt == "3":
	print "Evento pulsación larga\n"		#Pedir variable (dispositivo)
      elif opt == "4":
	print "Evento pulsación muy larga\n"		#Pedir variable (dispositivo)
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
    
    #SIGUIENTE: Incorporar comando final a enviar -> Ejem: E15:D01
