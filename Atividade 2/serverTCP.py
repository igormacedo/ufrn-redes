import socket, select

#classe para o usuario
class User:

    def __init__(self, socket):
        self.socket = socket
        self.nickname = None
    #troca o nome dos usuarios
    def changeNickname(self, name):
        self.nickname = name

#envia mensagens para todos, menos para o servidor e para o remetente
def broadcast(s,serverSocket,connections, msg):
    for socket in connections:
        if socket != serverSocket and socket != s:
            try:
                socket.send(msg)
            except:
                socket.close()
                connections.remove(socket)

#detecta o usuario a partir do seu socket
def detectUser(s,connections,users):
    for user in users:
        for socket in connections:
            if s == user.socket:
                return user
            else:
                continue


def main():
    # definicao das variaveis
    connections = [] #lista para armazenar conexoes, incluindo o servidor
    users = [] #lista para armazenar usuarios

    recvBuffer = 4096
    serverName = '0.0.0.0' # ip do servidor
    serverPort = 12000 # porta a se conectar
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # criacao do socket TCP
    serverSocket.bind((serverName,serverPort)) # bind do ip do servidor com a porta
    serverSocket.listen(10) # socket pronto para "ouvir" conexoes

    connections.append(serverSocket)

    print("Chat iniciado na porta {}".format(serverPort))

    while (1):
        #recebe a lista de sockets prontos para leitura
        readSockets, writeSockets,errorSockets = select.select(connections,[],[])
        for s in readSockets:
            #nova conexao
            if s == serverSocket:
                #conexao recebida atraves do serverSocket
                connectionSocket, addr = serverSocket.accept()

                u = User(connectionSocket)
                connectionSocket.send("Por favor, escolha um nickname \n")
                data = connectionSocket.recv(recvBuffer)

                while(not data):
                    connectionSocket.send("Nickname invalido. Por favor,escolha outro\n")
                    data = connectionSocket.recv(recvBuffer)

                u.changeNickname(data.rstrip('\n'))
                users.append(u)
                connections.append(connectionSocket)
                print("Cliente ({},{}), Nick {}".format(addr[0], addr[1], u.nickname))
                broadcast(connectionSocket,serverSocket,connections, "[{} entrou na sala]\n".format(u.nickname))
            #mensagem vindo de algum cliente
            else:
                u = detectUser(s,connections,users)
                try:
                    data = s.recv(recvBuffer)
                    if data:
                        if data.rstrip('\n') == '/listar':
                            s.send("Usuarios online: \n")
                            for i in range(0,len(users)):
                                s.send("{} - {}\n".format(i, users[i].nickname))
                        else:
                            broadcast(s,serverSocket,connections,'<{}> {}'.format(u.nickname, data))
                except:
                    broadcast(s,serverSocket,connections,"{} esta offline\n".format(u.nickname))
                    print("Cliente ({}:{}) esta offline".format(addr[0], addr[1]))
                    s.close()
                    connections.remove(s)
                    users.remove(u)
                    continue
    serverSocket.close()

if __name__ == "__main__":
    main()
