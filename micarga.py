#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import sys
import os
import time

# Mapear las opciones con su bloque de funcion
dic_options = {"Actuador" : f_actuadores,
           "Indicador" : f_indicadores,
           "Pulsador" : f_pulsadores,
           "Analogico" : f_analogicos
}

class modulo:
   nombreModulo = ""
   archivoModulo = ""
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
       self.pinescargados = {}    # crea una nueva lista vacía para cada modulo
       self.dicpines_str = {}	# además de otra para la copia en formato str.
       
       self.dicdispositivos = {}	# diccionario en el que guardar el nombre de cada actuador
       break
     
   def cargar(self):
     self.archivoModulo = self.nombreModulo
     self.archivoModulo += ".json"
     print "Nombre del archivo json del que cargar la configuración: {}".format(self.archivoModulo)
     try:
       with open(self.archivoModulo) as f:
	 self.pinescargados = json.load(f)
     except IOError:
       print "El módulo indicado no dispone de fichero de configuración, inicialícelo primero"
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
     return data
   
   def f_actuadores(self):
     print "1-Activar actuador \n2-Activar actuador durante cierto tiempo \n3-Desactivar el actuador"
     
   def f_indicadores(self):
     print "1-Activar indicador \n2-Activar durante cierto tiempo \n3-Activar con un tipo de parpadeo (tiempo apagado/tiempo encendido) \n4-Desactivar"
     
   def f_pulsadores(self):
     print "1-Evento pulsación simple \n2-Evento pulsación doble \n3-Evento pulsación larga \n4-Evento pulsación muy larga"
     
   def f_analogicos(self):
     print "1-Fijar umbrales mínimo y máximo \n2-Fijar histéresis \n3-Evento zona mínima \n4-Evento zona máxima \n5-Evento zona media"

####################################################################
## Programa principal
if __name__ == "__main__":
  device = modulo()
  
  device.cargar()
  
  device.to_str(device.pinescargados)
    
  print "Pines cargados convertidos a str: {}".format(device.dicpines_str)
  
  for k, v in device.dicpines_str.iteritems():
    if v != "":
      try:
	nombreDisp = raw_input("En el pin {} hay un {}. Distinguir como:>".format(k, v))
      except EOFError:
	print "--Saliendo del programa--"
	sys.exit(1)
      else:
	device.dicdispositivos[nombreDisp] = v
    else:
      print "Pin {} no asignado".format(k)
      
  print "---Nombre y clase de cada dispositivo:---\n {}\n".format(device.dicdispositivos)
  
  while True:
    try:
      interact = raw_input("Nombre del dispositivo con el que interactuar>")
    except EOFError:
      print "--Saliendo del programa--"
      sys.exit(1)
    if len(interact) == 0:
      continue
    
    if device.dicdispositivos.has_key(interact):
      print "El dispositivo '{}' es un {}.\n".format(interact, device.dicdispositivos[interact])
    else:
      print "El nombre de dispositivo indicado no existe, pruebe otra vez\n"
      continue
    print "Para el dispositivo '{}' existen las siguientes acciones:
    
    
