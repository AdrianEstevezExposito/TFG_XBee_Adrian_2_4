#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import sys
import os

class modulo:
   nombreModulo = ""
   archivoModulo = ""
   dicpines = {"1":"","2":"","3":"","4":"","5":"","6":"","7":"","8":"","9":"","10":"","11":"","12":"","13":"","14":"","15":"","16":"","17":"","18":"","19":"","20":""}
  # pinescargados = [] #Es posible que así esté mal instanciado
   
   
   def __init__(self):
        self.nombreModulo = raw_input("Nombre del módulo>")
        self.pinescargados = {}    # crea una nueva lista vacía para cada modulo

   """def pedirnombre(self):
     try:
       nombreModulo = raw_input("Nombre del módulo>")
     except EOFError: #EOF
       print "--Saliendo del programa--"
       sys.exit(1)
     else:
       archivoModulo = nombreModulo
       archivoModulo += ".json"
       print "Nombre del archivo json del que cargar: {}".format(archivoModulo) """
   
   def cargar(self):
     self.archivoModulo = self.nombreModulo
     self.archivoModulo += ".json"
     print "Nombre del archivo json del que cargar: {}".format(self.archivoModulo)
     with open(self.archivoModulo) as f:
       self.pinescargados = json.load(f)
     print "Pines cargados: {}".format(self.pinescargados)
     #Se muestran "u" que significan unicode, no tiene importancia. (CREO)

####################################################################
## Programa principal
if __name__ == "__main__":
  remoto = modulo()
  
  remoto.cargar()
