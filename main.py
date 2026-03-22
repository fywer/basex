"""
Punto de entrada principal del proyecto basex.

Uso:
    python main.py server                  → Inicia el servidor en 0.0.0.0:8080
    python main.py client <host> <port>    → Conecta un cliente al servidor
"""

import sys

from chat.servidor import Servidor
from client.cliente import Cliente


def main():
    """
    Punto de entrada principal.

    Parsea los argumentos de línea de comandos y ejecuta
    el servidor o el cliente según corresponda.
    """
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    modo = sys.argv[1].lower()

    if modo == "server":
        servidor = Servidor(host="0.0.0.0", port=8080)
        servidor.init()

    elif modo == "client":
        if len(sys.argv) < 4:
            sys.stderr.write(
                "Uso: python main.py client <host> <port>\n"
            )
            sys.exit(1)
        host = sys.argv[2]
        port = int(sys.argv[3])
        cliente = Cliente(host, port)
        cliente.start()

    else:
        sys.stderr.write(
            "Modo no reconocido: '{}'\n"
            "Usa 'server' o 'client'.\n".format(modo)
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
