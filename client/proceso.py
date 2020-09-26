from threading import Thread
import sys
class Proceso(Thread):
    cliente = None
    def __init__(self, cliente):
        Thread.__init__(self)
        self.cliente = cliente

    def run(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode()
                if mensaje == 'close':
                    self.cliente.close()
                    sys.stdout.write("Conexión Terminada.\n")
                    break
                else:
                    sys.stdout.write(mensaje + '\n')
            except Exception as e:
                sys.stderr.write(str(e) + '\n')
                break