"""
Módulo que define la clase Servidor.

El Servidor escucha conexiones TCP de clientes, crea un Proceso
(hilo) por cada cliente conectado, y gestiona el broadcast
de mensajes entre todos los clientes.
"""

import socket
import os
import sys

from utils import ahora, hoy, setup_logging
from chat.proceso import Proceso

LOG = setup_logging()

SLOGAN = '''
\t\t\t\t\t╔═════════════════════════╗ 
\t\t\t\t\t║     BASEX v.1.0.0 !..♥  ║ 
\t\t\t\t\t╚═════════════════════════╝
'''


class Servidor:
    """
    Servidor TCP para el chat basex.

    Acepta conexiones de clientes, crea un hilo (Proceso) por cada
    uno y gestiona el broadcast de mensajes entre ellos.

    Attributes:
        host: Dirección IP en la que escucha el servidor.
        port: Puerto en el que escucha el servidor.
        sock: Socket del servidor.
        procesos: Lista de procesos (clientes) activos.
    """

    def __init__(self, host="0.0.0.0", port=8080):
        """
        Inicializa el servidor con host y puerto.

        Args:
            host: Dirección IP para escuchar (default: 0.0.0.0).
            port: Puerto para escuchar (default: 8080).
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.procesos = []

    def init(self):
        """
        Inicia el servidor y comienza a aceptar conexiones.

        Enlaza el socket, escucha conexiones entrantes y crea
        un Proceso por cada cliente que se conecta.
        """
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            print(SLOGAN)
            LOG.info("{0} - - [{1} {2}] {3}\n".format(
                (self.host, self.port), hoy(), ahora(),
                "EL SERVIDOR HA INICIADO SU SERVICIO."
            ))
        except Exception as e:
            LOG.warning("ERROR: {0}\n".format(e))
            return

        try:
            while True:
                cliente, socketcliente = self.sock.accept()
                proceso = Proceso(self, cliente, len(self.procesos) + 1)
                LOG.info("{0} - - [{1} {2}] {3}\n".format(
                    socketcliente, hoy(), ahora(),
                    "EL SERVIDOR HA ACEPTADO UN CLIENTE."
                ))
                try:
                    nickname = cliente.recv(512).decode('ISO-8859-1').strip()
                    if len(nickname) < 1:
                        proceso.nickname = "anonymous"
                    else:
                        proceso.nickname = nickname
                    proceso.start()
                    self.procesos.append(proceso)
                    cliente.send(
                        " ^.^ BIENVENIDO @{0}\n".format(nickname).encode('ISO-8859-1')
                    )
                except Exception as e:
                    LOG.warning("ERROR (Accepting Client): {0}\n".format(e))
        except KeyboardInterrupt:
            LOG.info("Servidor detenido manualmente.")
        finally:
            self.sock.close()

    def users(self, emisor):
        """
        Envía al emisor la información del proceso asociado.

        Args:
            emisor: Socket del cliente que solicita la información.
        """
        for proceso in self.procesos:
            if emisor is proceso.cliente:
                emisor.send(repr(proceso).encode('ISO-8859-1'))

    def login(self, emisor):
        """
        Envía al emisor el nombre del usuario del sistema operativo.

        Args:
            emisor: Socket del cliente que solicita el login.
        """
        try:
            actor = os.getlogin()
        except OSError:
            actor = "unknown_user_docker"

        for proceso in self.procesos:
            if emisor is proceso.cliente:
                emisor.send(actor.encode('ISO-8859-1'))

    def quit(self, proceso):
        """
        Desconecta un proceso (cliente) del servidor.

        Args:
            proceso: Instancia de Proceso a desconectar.
        """
        try:
            proceso.cliente.close()
        except Exception:
            pass
        if proceso in self.procesos:
            self.procesos.remove(proceso)
        LOG.info("Se ha borrado de la memoria {}\n".format(proceso.cliente))

    def broadcast(self, emisor, mensaje):
        """
        Envía un mensaje a todos los clientes activos.

        Args:
            emisor: Socket del cliente que originó el mensaje.
            mensaje: Texto a difundir.
        """
        for proceso in self.procesos.copy():
            if proceso.status:
                receptor = proceso.cliente
                try:
                    receptor.send(mensaje.encode('ISO-8859-1'))
                except Exception as e:
                    LOG.warning("Error enviando mensaje via broadcast: {}".format(e))
                    self.quit(proceso)