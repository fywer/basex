"""
Módulo que define los hilos del cliente.

ServerListener escucha mensajes del servidor.
InputReader lee la entrada del usuario y la envía al servidor.
"""

from threading import Thread
import sys


class ServerListener(Thread):
    """
    Hilo que escucha mensajes provenientes del servidor.

    Se ejecuta como daemon para terminar automáticamente
    cuando el hilo principal finaliza.

    Attributes:
        sock: Socket conectado al servidor.
        stop_event: Evento de threading para señalizar la parada.
    """

    def __init__(self, sock, stop_event):
        """
        Inicializa el listener con el socket y evento de parada.

        Args:
            sock: Socket conectado al servidor.
            stop_event: threading.Event para coordinar la parada.
        """
        super().__init__()
        self.sock = sock
        self.stop_event = stop_event
        self.daemon = True

    def run(self):
        """
        Bucle principal: recibe datos del servidor y los muestra.

        Si recibe 'close', cierra la conexión y señaliza la parada.
        """
        while not self.stop_event.is_set():
            try:
                data = self.sock.recv(1024)
                if not data:
                    break
                mensaje = data.decode('ISO-8859-1')
                if mensaje == 'close':
                    self.sock.close()
                    sys.stdout.write("Conexión Terminada.\n")
                    self.stop_event.set()
                    break
                else:
                    sys.stdout.write("\r" + mensaje + "\n")
                    sys.stdout.flush()
            except Exception as e:
                if not self.stop_event.is_set():
                    sys.stderr.write("Error recibiendo datos: " + str(e) + '\n')
                break


class InputReader(Thread):
    """
    Hilo que lee la entrada del usuario y la envía al servidor.

    Se ejecuta como daemon para terminar automáticamente
    cuando el hilo principal finaliza.

    Attributes:
        sock: Socket conectado al servidor.
        nickname: Apodo del usuario.
        stop_event: Evento de threading para señalizar la parada.
    """

    def __init__(self, sock, nickname, stop_event):
        """
        Inicializa el lector de entrada.

        Args:
            sock: Socket conectado al servidor.
            nickname: Apodo del usuario.
            stop_event: threading.Event para coordinar la parada.
        """
        super().__init__()
        self.sock = sock
        self.nickname = nickname
        self.stop_event = stop_event
        self.daemon = True

    def run(self):
        """
        Bucle principal: lee input del usuario y lo envía al servidor.

        Si el usuario escribe 'quit', señaliza la parada.
        """
        while not self.stop_event.is_set():
            try:
                request = input("@{0}: ".format(self.nickname))
                if self.stop_event.is_set():
                    break
                self.sock.send(request.encode('ISO-8859-1'))
                if request.strip() == "quit":
                    self.stop_event.set()
                    break
            except EOFError:
                break
            except Exception as e:
                if not self.stop_event.is_set():
                    sys.stderr.write(str(e) + '\n')
                break