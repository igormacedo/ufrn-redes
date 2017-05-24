import socket

#envia mensagens para todos, menos para o servidor e para o remetente
def broadcast(s, msg):
    global connections
    for socket in connections:
        if socket != serverSocket and socket != s:
            try:
                socket.send(msg)
            except:
                socket.close()
                connections.remove(socket)


def main():
    # definicao das variaveis
    connections = [] #lista para armazenar conexoes, incluindo o servidor
    recvBuffer = 4096
    serverName = '' # ip do servidor (em branco)
    serverPort = 12000 # porta a se conectar
    serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # criacao do socket TCP
    serverSocket.bind((serverName,serverPort)) # bind do ip do servidor com a porta
    serverSocket.listen(1) # socket pronto para "ouvir" conexoes

    print("Chat iniciado na porta {}".format(serverPort))
   
    while 1:
        #recebe a lista de sockets prontos para leitura
        readSockets, writeSockets,errorSockets = select.select(connections,[],[])
        for s in readSockets:
            #nova conexão
            if s == serverSocket:
                #conexão recebida atraves do serverSocket
                connectionSocket, addr = serverSocket.accept()
                print("Cliente ({},{})".format(addr))
                broadcast(connectionSocket, "[{}:{} entrou na sala]".format(addr))
            #mensagem vindo de algum cliente
            else:
                try:
                    data = s.recv(4096)
                    if data:
                        broadcast(s, "\r" + '<' + str(s.getpeername()) + '> ' + data)
                except:
                    broadcast(s, "Cliente ({}:{}) esta offline".format(addr))
                    print("Cliente ({}:{}) esta offline".format(addr))
                    s.close()
                    connections.remove(s)
                    continue
    serverSocket.close()

if __name__ == '_main_':
    main()
