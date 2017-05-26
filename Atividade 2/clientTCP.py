import socket, select, string, sys

def prompt() :
    sys.stdout.write('<You> ')
    sys.stdout.flush()

#funcao principal
if(len(sys.argv) < 3) :
    print ('Como usar: python clientTCP.py host porta')
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)

#Conectar a um servidor
try :
    s.connect((host, port))
except :
    print ('Nao foi possivel se conectar')
    sys.exit()

print ('Conectado ao servidor.')

while (1):
    socketList = [sys.stdin, s]

    #recebe a lista de sockets prontos para leitura
    readSockets, writeSockets,errorSockets = select.select(socketList , [], [])

    for sock in readSockets:
        #mensagem vinda do servidor
        if sock == s:
            data = sock.recv(4096)
            if not data :
                print ('\nDesconectado do servidor')
                sys.exit()
            else:
                #print data
                sys.stdout.write(data)


        #mensagem enviada pelo cliente
        else :
            msg = sys.stdin.readline()
            s.send(msg)
