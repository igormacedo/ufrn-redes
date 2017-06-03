import sys
import socket
import select
import datetime,time
import threading as t


#variaveis globais
CLIENTS = {}
USERS = {}
TWOSEC = datetime.timedelta(seconds=2)
recvBuffer = 4096
kill = False

#classe para o usuario
class User:
    def __init__(self, addr):
        self.ip = addr[0]
        self.port = addr[1]
        self.nickname = None
        self.time = []
        self.block = False
        self.first = True
        #t.Thread(target=self.floodControl).start()
    #troca o nome dos usuarios
    def changeNickname(self, name):
        self.nickname = name
    #controle de flood
    def floodControl(self):
        if len(self.time) >= 5:
            if (self.time[4] - self.time[0]) <= TWOSEC and not self.block and self.first:
                print("init thread")
                t.Thread(target=self.floodthread).start()
    def floodthread(self):
        self.first = False
        self.block = True
        time.sleep(10)
        self.block = False
        self.first = True
        CLIENTS[str(self.ip)+":"+str(self.port)].send("Voce foi desbloqueado!")

#envia mensagens para todos, menos para o servidor e para o remetente
def broadcast(s, msg):
    print msg ## print message in server
    for socket in CLIENTS.values():
        if socket != s:
            try:
                socket.send(msg)
            except:
                socket.close()
                CLIENTS.pop(socket.fileno())

def clientConnection(clientSocket, user):

    id = str(user.ip)+":"+str(user.port)

    print "Thread do cliente " + str(user.ip) + ":" +str(user.port) + " iniciou"
    clientSocket.send("Por favor, escolha um nickname: ")
    data = clientSocket.recv(recvBuffer)

    while(data == ""):
        clientSocket.send("Nickname invalido. Por favor,escolha outro\n")
        data = clientSocket.recv(recvBuffer)

    user.changeNickname(data.rstrip('\n'))

    print("Cliente ({},{}), Nick {} entrou na sala".format(user.ip, user.port, user.nickname))

    clientSocket.send("Comandos do chat:")
    clientSocket.send("/listar - lista todos os usuarios")
    clientSocket.send("/trocarnick - muda o nickname")
    clientSocket.send("/sair - encerra o chat")

    broadcast(clientSocket, "[{} entrou na sala]\n".format(user.nickname))

    while not kill:
        # try:
        msg = clientSocket.recv(recvBuffer)
        if msg:
            if msg.rstrip('\n') == '/listar':
                clientSocket.send("Usuarios online:")
                for u in USERS.values():
                    clientSocket.send("<{},{},{}>".format(u.nickname, u.ip, u.port))

            elif msg.rstrip(msg[12:]) == '/trocarnick ':
                 newNick = msg[12:].rstrip('\n')
                 oldNick = user.nickname
                 user.changeNickname(newNick)
                 clientSocket.send("Voce mudou de {} para {}".format(oldNick, newNick))
                 broadcast(clientSocket, "{} mudou o nick para {}".format(oldNick, newNick))
                 print("Cliente ({},{}), Nick {}".format(user.ip, user.port, user.nickname))

            elif msg.rstrip('\n') == '/sair':
                broadcast(clientSocket,"{} saiu do chat".format(user.nickname))
                print("Cliente ({}:{}) esta offline".format(user.ip, user.port))
                clientSocket.send("kill")
                clientSocket.close()
                CLIENTS.pop(id)
                USERS.pop(id)
                break
            else:
                if user.block:
                    clientSocket.send("Voce foi bloqueado por 10s por motivos de: Flood")
                else:
                    broadcast(clientSocket,'<{}> {}'.format(user.nickname, msg))
                    if len(user.time) >= 5:
                        user.time.pop(0)
                        user.time.append(datetime.datetime.now())
                    else:
                        user.time.append(datetime.datetime.now())

                    user.floodControl()

        # except:
        #     broadcast(clientSocket,"{} esta offline".format(user.nickname))
        #     print("Cliente ({}:{}) esta offline".format(user.ip, user.port))
        #     clientSocket.close()
        #     CLIENTS.pop(id)
        #     USERS.pop(id)

def serverCommands(server):
    global kill
    while not kill:
        msg = raw_input()
        if msg == "/sair":
            for user in USERS.values():
                id = str(user.ip)+":"+str(user.port)
                CLIENTS[id].send("Abandon Ship! Server is going down!")
                CLIENTS[id].send("kill")
                CLIENTS[id].close()
                CLIENTS.pop(id)
                USERS.pop(id)
            kill = True
        else:
            print "Invalid command"



#codigo principal
def main():
    port = int(sys.argv[1])

    serverName = '0.0.0.0' # ip do servidor
    serverPort = port # porta a se conectar
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # criacao do socket TCP
    serverSocket.bind((serverName,serverPort)) # bind do ip do servidor com a porta
    serverSocket.listen(100) # socket pronto para "ouvir" conexoes

    print("Chat iniciado na porta {}".format(serverPort))

    t.Thread(target=serverCommands,
            name="serverCommands",
            args=(serverSocket,)).start()

    while not kill:

        serverSocket.setblocking(0)
        try:
            clientSocket, addr = serverSocket.accept()
            user = User(addr)

            id = str(user.ip)+":"+str(user.port)
            CLIENTS[id] = clientSocket
            USERS[id] = user

            t.Thread(target=clientConnection,
                    name="client"+str(addr[0])+":"+str(addr[1]),
                    args=(clientSocket, user)).start()

        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        kill = True
        print "Server exiting"
        print "Ctrl-c pressed in main..."
        sys.exit(1)
