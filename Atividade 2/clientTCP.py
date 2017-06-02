import socket
import string
import sys
import threading as t
import time

kill = False
block = False

def receiveData(conn):
    global kill
    while not kill:
        msg = conn.recv(4096)
        if msg == "kill":
            kill = True
            break
        elif msg == "block":
            block = True
        elif msg == "unblock":
            block = False
        print msg

def sendData(conn):
    global kill
    while not kill:
        if not block:
            msg = raw_input()
            conn.send(msg)
        else:
            print ("Voce foi bloqueado por flood, aguarde um pouco")

#funcao principal
if(len(sys.argv) < 3) :
    print ('Como usar: python clientTCP.py host porta')
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Conectar a um servidor
try :
    s.connect((host, port))
except :
    print ('Nao foi possivel se conectar')
    sys.exit()

print ('Conectado ao servidor.')


t.Thread(target=receiveData,
        name="receiveData",
        args=(s,)).start()

t.Thread(target=sendData,
        name="sendData",
        args=(s,)).start()

try:
    while not kill:
        time.sleep(1)

    print("Aplicacao terminada. Pressione [enter]")

except KeyboardInterrupt:
    kill = True
    print "Disconnected from server"
    print "Ctrl-c pressed in main..."
    sys.exit(1)

    #mensagem enviada pelo cliente
    #else :
        #msg = sys.stdin.readline()
        #s.send(msg)
