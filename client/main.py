from cliente import Cliente
import sys

def main():
    if len(sys.argv) > 2 :
        cliente = Cliente( str(sys.argv[1]), int(sys.argv[2]) )
    else:
        sys.stdout.write("No se han validados los argumentos.")

if __name__ == '__main__':
    main()