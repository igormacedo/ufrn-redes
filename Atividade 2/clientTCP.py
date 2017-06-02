import socket
import string
import sys
import threading as t
import time

kill = False

def receiveData(conn):
    global kill
    while not kill:
        try:
            msg = conn.recv(4096)
            if msg == "kill":
                kill = True
                break
            print msg
        except:
            pass

def sendData(conn):
    global kill
    while not kill:
        msg = raw_input()
        try:
            conn.send(msg)
        except:
            pass

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

s.setblocking(0)
print ('Conectado ao servidor.')


rec = t.Thread(target=receiveData,
        name="receiveData",
        args=(s,))
rec.daemon = True
rec.start()

sed = t.Thread(target=sendData,
        name="sendData",
        args=(s,))
sed.daemon = True
sed.start()

try:
    while not kill:
        time.sleep(1)

    print("Aplicacao terminada!")
    sys.exit(1)

except KeyboardInterrupt:
    kill = True
    print "Disconnected from server"
    print "Ctrl-c pressed in main..."
    sys.exit(1)

    #mensagem enviada pelo cliente
    #else :
        #msg = sys.stdin.readline()
        #s.send(msg)
