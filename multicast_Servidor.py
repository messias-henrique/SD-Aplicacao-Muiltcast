import socket
import struct
import threading
import time
from threading import Timer
import sys
 
GRUPO_MULTICAST_CLIENTE_SERVIDOR = '224.0.0.1'
PORTA_RECEBE = 5000
PORTA_ENVIA = 5002

GRUPO_MULTICAST_SERVIDORES = '224.0.0.2'
PORTA_SERVIDOR = 5001

ID_SERVIDOR = int(sys.argv[1]) # ID do servidor atual passado como argumento na linha de comando.
menorID = [] #Menor ID entre os servidores ativos.

# -- Comunicação com o(s) outro(s) servidores --------------------------------------------
def verificaIds():
    while True:
        enviaID()
        recebeID()

def enviaID():
    MULTICAST_TTL = 2
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Cria uma novo socket, dada a address family, tipo de socket e numero de protocolo.
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    sock.sendto(str(ID_SERVIDOR).encode(), (GRUPO_MULTICAST_SERVIDORES, PORTA_SERVIDOR)) # Envia os dados ao socket

def recebeID():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((GRUPO_MULTICAST_SERVIDORES, PORTA_SERVIDOR)) #conecta o socket a porta
    mreq = struct.pack("4sl", socket.inet_aton(GRUPO_MULTICAST_SERVIDORES), socket.INADDR_ANY) # .pack retorna um objeto em bytes transformados de acordo com o formato
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq) # .setsockopt modifica o valor de uma dada opção de socket e informa o SO que queremos os dados do endereço informado
    id_recebido = sock.recv(10240).decode() # recebe os dados pelo socket em bytes, e os transforma de volta em dados úteis
    i = int(id_recebido)
    if (i < ID_SERVIDOR) and (menorID.count(str(i)) == 0): # se o ID recebido é menor que o do servidor atual e não está inserido na lista
        menorID.insert(0, 'ID ' + str(i)) # insere no começo
# ----------------------------------------------------------------------------------------

# -- Comunicação com o Cliente -----------------------------------------------------------
def enviarResultado(msg, porta):
    MULTICAST_TTL = 2
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    sock.sendto(str(msg).encode(), (GRUPO_MULTICAST_CLIENTE_SERVIDOR, porta))

def receberExpressao(porta):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((GRUPO_MULTICAST_CLIENTE_SERVIDOR, porta))
    mreq = struct.pack("4sl", socket.inet_aton(GRUPO_MULTICAST_CLIENTE_SERVIDOR), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock.recv(10240).decode()

def escutarRequisicoes():
    while True:
        mensagem = receberExpressao(PORTA_RECEBE)
        print('\n[Expressão: ' + mensagem+']')
        if (not menorID): # se a lista esta vazia a maquina atual é a de menor ID e deve responder
            try: 
                resultado = eval(mensagem) # cálculo da expressão
            except:
                resultado = 'Expressão inválida.'
            finally:
                print('\n< Enviando resposta: '+str(resultado)+' >')
                enviarResultado('Resposta: '+str(resultado)+' (Enviado pelo servidor com ID <'+str(ID_SERVIDOR)+'>)', PORTA_ENVIA)

        else: continue
# ----------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------
print("\nServidor inicializado.\n")
print("\nID do servidor: <"+str(ID_SERVIDOR)+">\n")

enviaIds = threading.Thread(target=enviaID)
enviaIds.start()

requisicoes = threading.Thread(target=escutarRequisicoes)
requisicoes.start()

verifica = threading.Thread(target=verificaIds)
verifica.start()


while True:
    time.sleep(0.1)
    t = Timer(0.2, enviaID)
    t.start() 
    t2 = Timer(0.2, recebeID)
    t2.start() 
    t3 = Timer(0.5, menorID.clear)
    t3.start()
# ----------------------------------------------------------------------------------------