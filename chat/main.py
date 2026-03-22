from chat.servidor import Servidor

def main():
    servidor = Servidor(host="0.0.0.0", port=8080)
    servidor.init()

if __name__ == "__main__":
    main()