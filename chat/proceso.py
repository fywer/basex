"""
Módulo que define la clase Proceso.

Un Proceso representa la conexión activa de un cliente en el servidor.
Se ejecuta como un hilo (Thread) que escucha mensajes del cliente
y los procesa (broadcast, comandos del sistema, etc.).
"""

from threading import Thread, Lock
import subprocess
import sys

# Tiempo máximo de ejecución de un comando (en segundos)
COMMAND_TIMEOUT = 10

from utils import ahora, hoy


class Proceso(Thread):
    """
    Representa un cliente conectado al servidor.

    Hereda de Thread para ejecutarse en su propio hilo.
    Escucha mensajes del cliente, ejecuta comandos y
    difunde los resultados vía broadcast.

    Attributes:
        servidor: Instancia de Servidor que gestiona este proceso.
        _cliente: Socket del cliente conectado.
        id: Identificador único del proceso.
        fecha: Fecha de creación del proceso.
        tiempo: Hora de creación del proceso.
        _status: Estado activo/inactivo del proceso.
        _nickname: Apodo del usuario conectado.
    """

    def __init__(self, servidor, cliente, uid):
        """
        Inicializa el proceso con su servidor, socket de cliente e ID.

        Args:
            servidor: Instancia de Servidor que gestiona este proceso.
            cliente: Objeto socket del cliente.
            uid: Identificador único del proceso.
        """
        super().__init__()
        self.servidor = servidor
        self._cliente = cliente
        self.id = uid
        self.fecha = hoy()
        self.tiempo = ahora()
        self._status = True
        self._nickname = "@"
        self._mutex = Lock()

    def __repr__(self):
        """Retorna representación JSON del proceso."""
        import json
        p = {
            "id": self.id,
            "nickname": self._nickname,
            "fecha": self.fecha,
            "tiempo": self.tiempo,
            "estado": self._status
        }
        return json.dumps(p)

    @property
    def status(self):
        """Estado activo/inactivo del proceso."""
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def nickname(self):
        """Apodo del usuario conectado."""
        return self._nickname

    @nickname.setter
    def nickname(self, value):
        self._nickname = value

    @property
    def cliente(self):
        """Socket del cliente conectado."""
        return self._cliente

    def run(self):
        """
        Bucle principal del proceso.

        Escucha mensajes del cliente y los procesa:
        - 'quit': Desconecta al cliente.
        - '#users': Muestra usuarios activos.
        - '#login': Muestra usuario del sistema.
        - Cualquier otro texto: Se ejecuta como comando del sistema
          y el resultado se difunde vía broadcast.
        """
        try:
            self.servidor.broadcast(
                self._cliente,
                " ^.^ Se ha conectado... {0} ".format(self._nickname)
            )
        except Exception as e:
            sys.stderr.write("ERROR: {}\n".format(e))
            return

        while True:
            try:
                data = self._cliente.recv(512)
                if not data:
                    self.servidor.quit(self)
                    break

                mensaje = data.decode('ISO-8859-1').strip()

                if mensaje == "quit":
                    self._cliente.send("close".encode('ISO-8859-1'))
                    self.servidor.quit(self)
                    break

                if mensaje == "#users":
                    self.servidor.users(self._cliente)
                    continue

                if mensaje == "#login":
                    self.servidor.login(self._cliente)
                    continue

                # Ejecutar comando del sistema con timeout
                try:
                    response = subprocess.run(
                        mensaje,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True,
                        timeout=COMMAND_TIMEOUT
                    )
                    stdout = response.stdout
                    stderr = response.stderr
                except subprocess.TimeoutExpired as te:
                    # Capturar salida parcial del proceso que excedió el timeout
                    stdout = te.stdout or b''
                    stderr = te.stderr or b''
                    if not stdout and not stderr:
                        stderr = "Timeout: el comando excedió {} segundos.\n".format(
                            COMMAND_TIMEOUT
                        ).encode('ISO-8859-1')

                with self._mutex:
                    if len(stdout) > 0:
                        output = "\n@{0}: {1}\n".format(
                            self._nickname,
                            stdout.decode('ISO-8859-1', errors='ignore')
                        )
                    elif len(stderr) > 0:
                        output = "\n@{0}: Error: {1}\n".format(
                            self._nickname,
                            stderr.decode('ISO-8859-1', errors='ignore')
                        )
                    else:
                        output = "\n@{0}: {1}\n".format(
                            self._nickname,
                            "Advertencia: No se ha encontrado la salida estandar.\n"
                        )
                    self.servidor.broadcast(self._cliente, output)

            except Exception as e:
                sys.stderr.write("ERROR RUN: {}\n".format(e))
                self.servidor.quit(self)
                break