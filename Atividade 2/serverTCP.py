import sys
import socket
import select
import datetime
import threading as t


#variaveis globais
CLIENTS = {}
USERS = {}
recvBuffer = 4096

#classe para o usuario
class User:
    def __init__(self, addr):
        self.ip = addr[0]
        self.port = addr[1]
        self.nickname = None
    #troca o nome dos usuarios
    def changeNickname(self, name):
        self.nickname = name

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

#detecta o usuario a partir de uma porta
def detectUser(s,users):
    u = None
    for i in range(0,len(users)):
        if s == users[i].port:
            u = users[i]
            break
        else:
            continue
    return u

#gerencia os floods
def flood(socket, date, floodList, dateList):

        sec = datetime.timedelta(seconds=2)
        floodList.append(socket)
        dateList.append(date)

        if(len(floodList) == 2 and floodList[0] != floodList[1]):
            floodList[:] = []
            dateList[:] = []
            return false
        elif len(floodList) == 5 and (dateList[4]-dateList[0] <= sec):
            f = (floodList[1:] == floodList[:-1])
            floodList[:] = []
            dateList[:] = []
            return f
        elif len(floodList) == 5 and not (dateList[4]-dateList[0] <= sec):
            floodList[:] = []
            dateList[:] = []
            return False
        else:
            return False

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

    clientSocket.send("Comandos do chat: \n")
    clientSocket.send("/listar - lista todos os usuarios\n")
    clientSocket.send("/trocarnick - muda o nickname\n")
    clientSocket.send("/sair - encerra o chat\n")

    broadcast(clientSocket, "[{} entrou na sala]\n".format(user.nickname))

    while True:
        try:
            msg = clientSocket.recv(recvBuffer)
            if msg:
                if msg.rstrip('\n') == '/listar':
                    clientSocket.send("Usuarios online: \n")
                    for u in USERS.values():
                        clientSocket.send("<{},{},{}>\n".format(u.nickname, u.ip, u.port))

                elif msg.rstrip(msg[12:]) == '/trocarnick ':
                     newNick = msg[12:].rstrip('\n')
                     oldNick = user.nickname
                     u.changeNickname(newNick)
                     clientSocket.send("Voce mudou de {} para {}\n".format(oldNick, newNick))
                     broadcast(clientSocket, "{} mudou o nick para {}\n".format(oldNick, newNick))
                     print("Cliente ({},{}), Nick {}".format(user.ip, user.port, user.nickname))

                elif msg.rstrip('\n') == '/sair':
                    broadcast(clientSocket,"{} saiu do chat\n".format(user.nickname))
                    print("Cliente ({}:{}) esta offline".format(user.ip, user.port))
                    clientSocket.send("kill")
                    clientSocket.close()
                    CLIENTS.pop(id)
                    USERS.pop(id)
                    break
                else:
                    broadcast(clientSocket,'<{}> {}'.format(user.nickname, msg))
        except :
            broadcast(clientSocket,"{} esta offline\n".format(user.nickname))
            print("Cliente ({}:{}) esta offline".format(user.ip, user.port))
            clientSocket.close()
            CLIENTS.pop(id)
            USERS.pop(id)

#codigo principal
def main():
    port = int(sys.argv[1])

    serverName = '0.0.0.0' # ip do servidor
    serverPort = port # porta a se conectar
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # criacao do socket TCP
    serverSocket.bind((serverName,serverPort)) # bind do ip do servidor com a porta
    serverSocket.listen(100) # socket pronto para "ouvir" conexoes

    print("Chat iniciado na porta {}".format(serverPort))

    while (1):

        clientSocket, addr = serverSocket.accept()
        user = User(addr)

        id = str(user.ip)+":"+str(user.port)
        CLIENTS[id] = clientSocket
        USERS[id] = user

        t.Thread(target=clientConnection,
                name="client"+str(addr[0])+":"+str(addr[1]),
                args=(clientSocket, user)).start()

if __name__ == "__main__":
    main()
