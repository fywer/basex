"""
Módulo que define la clase Cliente.

El Cliente se conecta al servidor TCP, envía un nickname,
y lanza dos hilos: uno para escuchar mensajes del servidor
y otro para leer la entrada del usuario.
"""

import socket
import sys
from threading import Event

from client.proceso import ServerListener, InputReader


class Cliente:
    """
    Cliente TCP para el chat basex.

    Se conecta al servidor, envía un nickname y gestiona
    la comunicación mediante dos hilos independientes.

    Attributes:
        host: Dirección IP del servidor.
        port: Puerto del servidor.
        sock: Socket de la conexión.
        nickname: Apodo del usuario.
    """

    def __init__(self, host, port):
        """
        Inicializa el cliente con host y puerto del servidor.

        Args:
            host: Dirección IP del servidor.
            port: Puerto del servidor.
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""

    def start(self):
        """
        Inicia la conexión al servidor y lanza los hilos de comunicación.

        Solicita un nickname al usuario, se conecta al servidor,
        y crea dos hilos daemon:
        - ServerListener: escucha mensajes del servidor.
        - InputReader: lee entrada del usuario.

        El hilo principal espera hasta que alguno de los dos hilos
        señale la finalización mediante el stop_event.
        """
        try:
            self.sock.connect((self.host, self.port))
            while True:
                nickname = input("INGRESA UN NICKNAME: ").strip()
                if len(nickname) > 0:
                    break
            self.nickname = nickname
            self.sock.send(nickname.encode('ISO-8859-1'))
        except Exception as e:
            sys.stderr.write("Error de conexion: " + str(e) + '\n')
            return

        stop_event = Event()

        listener = ServerListener(self.sock, stop_event)
        listener.start()

        reader = InputReader(self.sock, self.nickname, stop_event)
        reader.start()

        # El hilo principal espera hasta que alguno de los dos hilos señale el fin
        stop_event.wait()
        try:
            self.sock.close()
        except Exception:
            pass