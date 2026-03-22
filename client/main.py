"""Módulo de entrada del cliente basex (ejecución directa)."""

import sys

from client.cliente import Cliente


def main():
    """Punto de entrada para ejecutar el cliente directamente."""
    if len(sys.argv) > 2:
        cliente = Cliente(str(sys.argv[1]), int(sys.argv[2]))
        cliente.start()
    else:
        sys.stdout.write(
            "No se han validado los argumentos. "
            "Uso: python -m client.main <host> <port>\n"
        )


if __name__ == '__main__':
    main()