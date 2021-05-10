import socket
import struct

GRUPO_MULTICAST = '224.0.0.1'
PORTA_ENVIA = 5000
PORTA_RECEBE = 5002

#-------------------------------------------------------------------------------------
def enviarExpressao(mensagem):
    print('Enviando expressão -> ' + str(mensagem))
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # Cria uma novo socket, dada a address family, tipo de socket e numero de protocolo.
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    sock.sendto(str(mensagem).encode(), (GRUPO_MULTICAST, PORTA_ENVIA))

def receberResposta():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # .setsockopt modifica o valor de uma dada opção de socket e informa o SO que queremos os dados do endereço informado
    sock.bind((GRUPO_MULTICAST, PORTA_RECEBE))
    mreq = struct.pack("4sl", socket.inet_aton(GRUPO_MULTICAST), socket.INADDR_ANY) # .pack retorna um objeto em bytes transformados de acordo com o formato
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    resposta = sock.recv(10240).decode()  # recebe os dados pelo socket em bytes, e os transforma de volta em dados úteis
    print(resposta)
#-------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        expressao = input("Expressão -> ")
        enviarExpressao(expressao) #Envia a expressão para os servidores
        receberResposta() #Escuta as requisições de respostas dos servidores
#-------------------------------------------------------------------------------------