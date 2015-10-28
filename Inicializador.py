#!/usr/bin/python
# -*- coding: UTF-8 -*-

import readline
import json
import time
import sys
import os

dicpines = {"1":"","2":"","3":"","4":"","5":"","6":"","7":"","8":"","9":"","10":"","11":"","12":"","13":"","14":"","15":"","16":"","17":"","18":"","19":"","20":""}

dicdisp = {"1":"Indicador","2":"Actuador","3":"Pulsador","4":"Analogico"}
flag = 0

while True:
  try:
    name = raw_input("Nombre del módulo>")
  except EOFError: #EOF
    print "--Saliendo del programa--"
    break
  else:
    name += ".json"
    if name == "exit.json":
      print "--Saliendo del programa--"
      break
  while True:
    time.sleep(1)
    try:
      s = raw_input("Especifique pin a definir> ")
    except EOFError: #EOF
      print "--Saliendo a Inicio del Programa--"
      break
    if s == "exit":
      if flag == 1:
	os.remove("data.json")
	flag = 0
      print "--Saliendo a Inicio del Programa--"
      break
    if s == "save":
      if flag == 1:
	g = raw_input("¿Guardar json?(s/n)> ")
	if g == "s":
	  os.rename("data.json",name)
	  flag = 0
	  break
	else:
	  os.remove("data.json")
	  flag = 0
	  break
      else:
	break
    try:
      int(s)
    except ValueError:
      print "No es un numero"
      continue
    if 20>=int(s) and int(s)>0:
      print "Pin correcto"
    else:
      print "Pin incorrecto:{}".format(s)
      continue
    try:
      si = raw_input(" 1:Indicador(led)\n 2:Actuador(rele)\n 3:Pulsador\n 4:Señal Analogica(potenciometro)\n > ")
    except EOFError: #EOF
      break
    if len(s) == 0:
      continue
    int(si)
    if int(si)<=4 and int(si)>0:
      print "Dispositivo correcto"
    else:
      print "Dispositivo incorrecto:{}".format(si)
      continue
    print "Inicialización definida: Pin = {}; Dispositivo = {}".format(s,si)
    dicpines[s] = dicdisp[si]
    print "El diccionario se volcará así:\n {}".format(dicpines)
    with open('data.json', 'w') as outfile:
      json.dump(dicpines, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
    flag = 1

    
