#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import sys
import os

class modulo:
   nombreModulo = ""
   archivoModulo = ""
   dicpines = {"1":"","2":"","3":"","4":"","5":"","6":"","7":"","8":"","9":"","10":"","11":"","12":"","13":"","14":"","15":"","16":"","17":"","18":"","19":"","20":""}
   pinescargados = []
   
   def pedirnombre(self):
     try:
       nombreModulo = raw_input("Nombre del módulo>")
     except EOFError: #EOF
       print "--Saliendo del programa--"
       break
     else:
       archivoModulo = nombreModulo
       archivoModulo += ".json"
       print "Nombre del archivo json del que cargar: {}".format(archivoModulo) 
   
   def cargar(self):  
     with open(archivoModulo) as f:
       for line in f:
	 pinescargados.append(json.loads(line))
     print "Pines cargados: {}".format(pinescargados) 
        
remoto = modulo()

remoto.pedirnombre()

remoto.cargar()
