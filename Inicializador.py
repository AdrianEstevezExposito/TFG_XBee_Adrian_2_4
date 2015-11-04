#!/usr/bin/python
# -*- coding: UTF-8 -*-

import readline
import json
import time
import sys
import os

dicpines = {"1":"","2":"","3":"","4":"","5":"","6":"","7":"","8":"","9":"","10":"","11":"","12":"","13":"","14":"","15":"","16":"","17":"","18":"","19":"","20":""}

dicpines_vacio = {"1":"","2":"","3":"","4":"","5":"","6":"","7":"","8":"","9":"","10":"","11":"","12":"","13":"","14":"","15":"","16":"","17":"","18":"","19":"","20":""}

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
  print "--AYUDA: Use los comandos 'save' y 'exit' para guardar y salir--."
  while True:
    time.sleep(1)
    try:
      s = raw_input("Especifique pin a definir> ")
    except EOFError: #EOF
      print "--Saliendo a Inicio del Programa--"
      if flag == 1:
	print "--Borrando configuración del módulo--"
	os.remove("data.json")
	for k, v in dicpines.iteritems():
	  if v != "":
	    dicpines[k] = ""
	flag = 0
      break
    if s == "exit":
      if flag == 1:
	print "--Borrando configuración del módulo--"
	os.remove("data.json")
	for k, v in dicpines.iteritems():
	  if v != "":
	    dicpines[k] = ""
	flag = 0
      print "--Saliendo a Inicio del Programa--"
      break
    if s == "save":
      if flag == 1:
	guar = raw_input("¿Guardar configuración?(s/n)> ")
	if guar == "s":
	  os.rename("data.json",name)
	  for k, v in dicpines.iteritems():
	    if v != "":
	      dicpines[k] = ""
	  flag = 0
	  break
	else:
	  borr = raw_input("¿Borrar configuración?(s/n)> ")
	  if borr == "s":
	    print "--Borrando configuración del módulo--"
	    os.remove("data.json")
	    for k, v in dicpines.iteritems():
	      if v != "":
		dicpines[k] = ""
	    flag = 0
	    break
	  else:
	    print "No se ha borrado la configuración. Continuamos inicializando. "
	    continue
      else:
	print "No hay nada que guardar"
	continue
    try:
      int(s)
    except ValueError:
      print "No es un número"
      continue
    if 20>=int(s) and int(s)>0:
      print "Pin correcto"
    else:
      print "Pin incorrecto:{}".format(s)
      continue
    try:
      si = raw_input(" 1:Indicador(led)\n 2:Actuador(rele)\n 3:Pulsador\n 4:Señal Analogica(potenciometro)\n > ")
    except EOFError: #EOF
      if flag == 1:
	print "--Borrando configuración del módulo--"
	os.remove("data.json")
	for k, v in dicpines.iteritems():
	  if v != "":
	    dicpines[k] = ""
	flag = 0
      print "--Saliendo a Inicio del programa--"
      break
    if len(si) == 0:
      print "Inicialización definida: Borrado del Pin = {}".format(s)
      dicpines[s] = si
      print "El diccionario se volcará así:\n {}".format(dicpines)
      with open('data.json', 'w') as outfile:
	json.dump(dicpines, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
      flag = 1
      continue
    try:
      int(si)
    except ValueError:
      print "No es un número"
      continue
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

    
