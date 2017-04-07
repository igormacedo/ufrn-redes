# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTOR: PROF. CARLOS M D VIEGAS (viegas 'at' dca.ufrn.br)
#
# SCRIPT: Base de um servidor HTTP
# ALTERADO POR: IGOR MACEDO SILVA

# importacao das bibliotecas
import socket
import os

# definicao do host e da porta do servidor
HOST = '' # ip do servidor (em branco)
PORT = 8080 # porta do servidor

http_response200 = """\
HTTP/1.1 200 OK

[page]
"""

http_response404 = """\
HTTP/1.1 404 Not Found\r\n\r\n

<html><head></head><body><h1>404 Not Found</h1></body></html>\r\n
"""

http_response400 = """\
HTTP/1.1 404 Bad Request\r\n\r\n

<html><head></head><body><h1>400 Bad Request</h1></body></html>\r\n
"""

def getPage(path):
    if path == "/":
        page = open("index.html","r")
        content = page.read()
        page.close
        return content

    elif os.path.exists(path.strip("/")+".html"):
        page = open(path.strip("/")+".html","r")
        content = page.read()
        page.close
        return content

    else:
        return None

# cria o socket com IPv4 (AF_INET) usando TCP (SOCK_STREAM)
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# permite que seja possivel reusar o endereco e porta do servidor caso seja encerrado incorretamente
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# vincula o socket com a porta (faz o "bind" do IP do servidor com a porta)
listen_socket.bind((HOST, PORT))

# "escuta" pedidos na porta do socket do servidor
listen_socket.listen(1)

# imprime que o servidor esta pronto para receber conexoes
print 'Servidor HTTP aguardando conexoes na porta %s ...' % PORT

while True:
    # aguarda por novas conexoes
    client_connection, client_address = listen_socket.accept()
    # o metodo .recv recebe os dados enviados por um cliente atraves do socket
    request = client_connection.recv(1024)
    vector_request = request.split(" ")
    print request

    if len(vector_request) < 3: # se nao houver tres elementos no request
        http_response = http_response400 # retorna Bad Request Error

    elif (not(vector_request[0].startswith("get") or vector_request[0].startswith("GET"))):
        http_response = http_response400

    elif (getPage(vector_request[1]) == None):
        http_response = http_response404

    else:
        page = getPage(vector_request[1])
        print(page)
        http_response = http_response200.replace("[page]",page)
        # imprime na tela o que o cliente enviou ao servidor

    # servidor retorna o que foi solicitado pelo cliente (neste caso a resposta e generica)
    client_connection.send(http_response)
    # encerra a conexao
    client_connection.close()

# encerra o socket do servidor
listen_socket.close()
