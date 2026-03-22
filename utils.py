"""
Módulo de utilidades compartidas para el proyecto basex.

Proporciona funciones de fecha/hora y configuración de logging
utilizadas tanto por el servidor como por el cliente.
"""

import time
import sys
import logging


def ahora():
    """Retorna la hora actual en formato HH:MM:SS."""
    return time.ctime().split(' ')[3]


def hoy():
    """Retorna la fecha actual en formato Mes/Día/Año."""
    items = time.ctime().split(' ')
    return "{0}/{1}/{2}".format(items[1], items[2], items[4])


def setup_logging(level=logging.DEBUG):
    """
    Configura el logging global del proyecto.

    Args:
        level: Nivel de logging (default: DEBUG).

    Returns:
        Logger configurado.
    """
    logging.basicConfig(
        level=level,
        format='%(levelname)7s : %(message)s',
        stream=sys.stderr,
    )
    return logging.getLogger('')
