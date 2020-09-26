from threading import Thread
from threading import Lock
import subprocess
import time
import json
import sys

ahora = lambda: time.ctime().split(' ')[3]
hoy = lambda items=time.ctime().split(' '): "{0}/{1}/{2}".format(items[1], items[2], items[4])

class Proceso(Thread):
    servidor = None
    mutex = Lock()
    def __init__(self, servidor, cliente, uid):
        '''Asocia un objeto socket al proceso,
		genera su identificador en función de la cantidad de procesos activos,
		almacena la fecha y hora en el momento que se crea el proceso y activa su estado a verdadero.

		Argumentos/parámetros
		cliente - - Objeto tipo socket del cliente
		retorna: None
		'''
        Thread.__init__(self)
        self.servidor = servidor
        self.cliente = cliente
        self.id = uid
        self.fecha = hoy()
        self.tiempo = ahora()
        self.status = True
        self.nickname = "@"

    def __repr__(self):
        p = {
            "id": self.id,
            "nickname": self.nickname,
            "fecha": self.fecha,
            "tiempo": self.tiempo,
            "estado": self.status
        }
        return json.dumps(p)

    def getId(self):
        '''Devuelve el id del proceso.

        Argumentos/parámetros
		retorna: int
		'''
        return self.id

    def getStatus(self):
        '''Devuelve el estado del proceso.

		Argumentos/parámetros
		retorna: bool
		'''
        return self.status

    def getNickname(self):
        '''Devuelve el nombre del proceso.

		Argumentos/parámetros
		retorna: str
		'''
        return self.nickname

    def setNickname(self, nickname):
        '''
		'''
        self.nickname = nickname

    def setStatus(self, status):
        '''
        '''
        self.status = status

    def getCliente(self):
        '''

		Argumentos/parámetros
		retorna: socket.socket
		'''
        return self.cliente

    def getServidor(self):
        '''
        '''
        return self.servidor
    
    def run(self):
        ''' Recupera mensajes del cliente,
		si el mensaje es igual a "#users" desplegará los usuarios en estado activo
		el servidor restructura el mensaje y ejecuta la función broadcast.
		Argumentos/parámetros
		retorna: None
		'''
        try:
            self.getServidor().broadcast(self.getCliente(), " ^.^ Se ha conectado... {0} ".format(self.getNickname()))
        except Exception as e:
            sys.stderr.write("ERROR: {}\n".format(e))
            return

        while True:
            try:
                mensaje = self.getCliente().recv(512).decode('ISO-8859-1').strip()
                if mensaje == "quit":
                    self.getCliente().send("close".encode())
                    self.getServidor().quit(self)
                    break
                    # De no usar el break lanza el error OSError
                if mensaje == "#users":
                    self.getServidor().users(self.getCliente())
                    pass 
                if mensaje == "#login":
                    self.getServidor().login(self.getCliente())
                    pass
                else:
                    comandos = mensaje.split(" ")
                    response = subprocess.run(comandos, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    #self.mutex.acquire()
                    if not len(response.stdout) <= 0:
                        output = "\n@{0}: {1}\n".format(self.getNickname(), response.stdout.decode('ISO-8859-1'))
                        self.getServidor().broadcast(self.getCliente(), output)
                    elif not len(response.stderr) <= 0:
                        output = "\n@{0}: Error: {1}\n".format(self.getNickname(), response.stderr.decode('ISO-8859-1'))
                        self.getServidor().broadcast(self.getCliente(), output)
                    else:
                        output = "\n@{0}: {1}\n".format(self.getNickname(), "Advertencia: No se ha encontrado la salida estandar.\n")
                        self.getServidor().broadcast(self.getCliente(), output)
                    #self.mutex.release()
            except Exception as e:
                sys.stderr.write("ERROR: {}\n".format(e))
                break
                #self.servidor.quit(self)