import socket
import sys
import time
import os
import logging
from chat.proceso import Proceso


ahora = lambda: time.ctime().split(' ')[3]
hoy = lambda items=time.ctime().split(' '): "{0}/{1}/{2}".format(items[1], items[2], items[4])
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)7s : %(message)s',
    stream = sys.stderr,
)
LOG = logging.getLogger('')
slogan = '''
\t\t\t\t\t╔═════════════════════════╗ 
\t\t\t\t\t║     BASEX v.1.0.0 !..♥  ║ 
\t\t\t\t\t╚═════════════════════════╝
'''
class Servidor(socket.socket):
    procesos = []
    def __init__(self):
        socket.socket.__init__(self)
        self.sock = ("0.0.0.0", 8080)

    def init(self):
        try:
            self.bind(self.sock)
            self.listen(1)
            print(slogan)
            LOG.info("{0} - - [{1} {2}] {3}\n".format(self.sock, hoy(), ahora(), "EL SERVIDOR HA INICIADO SU SERVICIO."))
        except Exception as e:
            LOG.warn("ERROR: {0}\n".format(e))
            return
        while True:
            cliente, socketcliente = self.accept()
            proceso = Proceso(self, cliente, len(self.procesos) + 1)
            LOG.info("{0} - - [{1} {2}] {3}\n".format(socketcliente, hoy(), ahora(), "EL SERVIDOR HA ACEPTADO UN CLIENTE."))
            try:
                nickname = cliente.recv(512).decode('ISO-8859-1').strip()
                if len(nickname) < 1:
                    proceso.setNickname("anonymous")
                else:
                    proceso.setNickname(nickname)
                proceso.start()
                self.procesos.append(proceso)
                cliente.send(" ^.^ BIENVENIDO @{0}\n".format(nickname).encode())
            except Exception as e:
                LOG.warn("ERROR: {0}\n".format(e))

    @classmethod
    def users(cls, emisor):
        for proceso in cls.procesos:
            if emisor is not proceso.getCliente():
                pass
            else:
                emisor.send(repr(proceso).encode())

    @classmethod
    def login(cls, emisor):
        for proceso in cls.procesos:
            if emisor is not proceso.getCliente():
                pass
            else:
                actor = os.getlogin()
                emisor.send(actor.encode())

    @classmethod
    def quit(cls, proceso):
        proceso.getCliente().close()
        cls.procesos.remove(proceso)
        LOG.info("Se ha borrado de la memoria {}\n".format(proceso.getCliente()))

    @classmethod
    def broadcast(cls, emisor, mensaje):
        for proceso in cls.procesos:
            if not proceso.getStatus():
                pass
            else:
                receptor = proceso.getCliente()
                receptor.send(mensaje.encode())