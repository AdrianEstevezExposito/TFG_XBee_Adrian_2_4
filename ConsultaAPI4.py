#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#Copyright © 2015  Alberto Hamilton Castro
#
#Este programa es software libre: usted puede redistribuirlo y/o modificarlo conforme a los términos
# de la Licencia Pública General de GNU publicada por la Fundación para el Software Libre,
# ya sea la versión 3 de esta Licencia o (a su elección) cualquier versión posterior.
#Este programa se distribuye con el deseo de que le resulte útil, pero SIN GARANTÍAS DE NINGÚN TIPO;
# ni siquiera con las garantías implícitas de COMERCIABILIDAD o APTITUD PARA UN PROPÓSITO DETERMINADO.
#Para más información, consulte la Licencia Pública General de GNU.



from Conexiones import *
from DialogaAPI2 import *
from micarga import *
import time
import sys
import re
import argparse
import readline

def hiloPrincipal( du ):
  parser = argparse.ArgumentParser()
  parser.add_argument("--port"
    , help="puerto de conexión", default="/dev/ttyUSB0" )
  parser.add_argument("--speed", type=int
    , help="velocidad de conexion", default=115200 )
  parser.add_argument("--log"
    , help="nivel de log", default="info" )


  args = parser.parse_args()

  numeric_level = getattr(logging, args.log.upper(), None)
  if not isinstance(numeric_level, int):
      raise ValueError('Invalid log level: %s' % loglevel)
  logging.basicConfig(level=numeric_level
    , format='%(asctime)s %(levelname)s:[%(funcName)s] %(message)s'
    )
  if args.port[0] == '/':
    #Usamos conexion serial local
    logging.info( "Conectando a {} con velocidad {}".format( args.port, args.speed ) )
    try:
      du.setConexion( conexion_ser(args.port,args.speed) )
    except:
      logging.critical( "Unexpected error: {}".format( sys.exc_info()[0] ) )
      logging.critical( "No se pudo conectar con Serial" )
      exit(1)
  else:
    #usamos conexion sock
    conex = args.port.split(":")
    host = "localhost"
    if len(conex) == 1:
      port = int(conex[0])
    elif conex[0] == "":
      port = int(conex[1])
    else:
      port = int(conex[1])
      host = conex[0]
    logging.info( "Conectando a {}:{}".format( host, port ) )
    try:
      du.setConexion( conexion_sock(host, port) )
    except:
      logging.critical( "Unexpected error: {}".format( sys.exc_info()[0] ) )
      logging.critical( "No se pudo conectar con SOCK" )
      exit(1)

  du.start()

  depura = False #indica estado de depuración que se puede cambiar
  Remoto = -1
  Breve = False #indica direcciones se muestran en modo breve


  cmds = 'SH, SL, VR, AI, OP, CH, NI, ND'
  print "Enviado comandos AT locales '{}' \n -Espere mientras se inicializa la configuración.".format(cmds)
  du.comandosATlocal( cmds )

  time.sleep(5)
  
  device.start()

  while device.stop:
    while not device.q.empty():
      s = device.q.get()
      
      sNorm = s.upper().strip()
      if sNorm=="DEBUG":
	depura = not depura
	print "\nEstado de depuración: {}\n".format( depura )
	if depura:
	  logging.getLogger().setLevel( logging.DEBUG )
	else:
	  logging.getLogger().setLevel( logging.INFO )
	continue
      if sNorm=="TABLA":
	print "\nTabla de nodos: {}\n".format( du.tablaDir2Str() )
	continue
      if sNorm=="BREVE":
	Breve = not Breve
	print "\nModo breve es: {}\n".format( Breve )
	du.setModoBreveRecepcion( Breve )
	continue

      #No es un comando vemos el tipo de AT
      m = re.search(r"([^:]*):(.*)", s)
      if m: #se ha utilizado los :
	( remota, comandos ) = m.groups()
	if len( remota )>0: #se epecifico nombre o dirección
	  #Probamos primero con el nombre
	  serial = du.nombretoSerial( remota )
	  if serial<0: #no se encontró nombre, tratamos dirección 16
	    serial = du.dir16toSerial( hexStr2Int( remota ) )
	  if serial<0:
	    print "Especificación remota '{}' no encontrada, NO enviamos".format( remota )
	    continue
	  Remoto = serial
	  print "Usando dirección remota 0x{:X}".format( Remoto )
	if Remoto<0:
	  print "No hay dirección remota válida almacenada, NO enviamos"
	  continue
	try:
	  #print "Enviando comandos: >{}<".format(comandos)
	  du.comandosATremoto( Remoto, -1, comandos )
	except:
	  print "Error al enviar comandos remotos '{}'".format( comandos )
      else: #No aparecen los :, es comando local
	try:
	  #print "Enviando comandos locales: >{}<".format(s)
	  du.comandosATlocal( s )
	except:
	  print "Error al enviar comandos locales '{}'".format( s )

  du.finish()
  du.join()
  logging.info( "Terminamos" )
  sys.exit(0)

####################################################################
## Programa principal
if __name__ == "__main__":
  
  device = modulo()
  
  device.cargar()
  
  device.to_str(device.pinescargados)	#Necesario convertir los valores en string para mejor manejo
  
  if device.check_config():
    device.nombrar()
  
  hiloPrincipal( dialogoAPI(None, device.q, device.q_T_Boton) )
  
