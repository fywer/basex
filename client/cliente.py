import socket
import sys
from proceso import Proceso

class Cliente(socket.socket):
    def __init__(self, nodo, puerto):
        socket.socket.__init__(self)
        self.sock = (nodo, puerto)
        try:
            self.connect(self.sock)
            while True:
                nickname = input("INGRESA UN NICKNAME: ")
                if len(nickname) < 1:
                    pass
                else:
                    break
            self.nickname = nickname
            self.send(nickname.encode())
            Proceso(self).start()
        except Exception as e:
            sys.stderr.write(str(e) + '\n')
            return
            
        while True:
            try:
                request = input("@{0}: ".format(self.nickname))
                self.send(request.encode())
            except Exception as e:
                sys.stderr.write(str(e) + '\n')
                break