#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import sys
import os
import time

class modulo:
   nombreModulo = ""
   archivoModulo = ""
  # pinescargados = [] #Es posible que así esté mal instanciado
   
   
   def __init__(self):
     try:
       self.nombreModulo = raw_input("Nombre del módulo>")
     except EOFError: #EOF
       print "--Saliendo del programa--"
       sys.exit(1)
     self.pinescargados = {}    # crea una nueva lista vacía para cada modulo
     self.dicpines_str = {}	# además de otra para la copia en formato str.
     
     self.dicdispositivos = {}	# diccionario en el que guardar el nombre de cada actuador
     
   def cargar(self):
     self.archivoModulo = self.nombreModulo
     self.archivoModulo += ".json"
     print "Nombre del archivo json del que cargar la configuración: {}".format(self.archivoModulo)
     with open(self.archivoModulo) as f:
       self.pinescargados = json.load(f)
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
      except EOFError: #EOF
	print "--Saliendo del programa--"
	sys.exit(1)
      else:
	device.dicdispositivos[nombreDisp] = v
    else:
      print "Pin {} no asignado".format(k)
  
  print "Nombre y clase de cada dispositivo:\n {}".format(device.dicdispositivos)
