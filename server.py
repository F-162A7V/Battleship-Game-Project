__author__ = "F-162A7V"



import socket, pickle, threading,hashlib, struct,pygame,os,tkinter
from ctypes.wintypes import PUINT

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding



stop = False



def makeSendableMsg(msg):
    try:
        msg = msg.encode()
    except:
        pass
    return struct.pack("I",len(msg)) + msg

def makeSendableENC(msg,key):
    return

def recieveData(sock):
    L = sock.recv(4)
    L = struct.unpack("I",L)[0]
    response = sock.recv(L)
    return response, response.split(b"--||||--")

def recieveENC(sock,key):
    return


def parse_msg(byteresp):
    return


#region Encryption
def RSAenc(data,public_key):
    encrypted_message = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_message

def encryptexchange(sock):
    resp,fields = recieveData(sock)
    AEKey = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(AEKey)
    if fields[0] == b'HELO':
        public_key = pickle.loads(fields[1])
        msg = b'AESK--||||--' + pickle.dumps(aesgcm)
        enc_msg = RSAenc(msg,public_key)
    else:
        sock.send(makeSendableMsg("EROR--||||--001"))
#endregion


def handle_client(sock,notuple):
    encryptexchange(sock)



def mainLoop(ip="127.0.0.1",port=11111):
    global stop
    sock = socket.socket()
    sock.bind((ip,port))
    sock.listen(100000)
    threads = []
    while not stop:
        c,a = sock.accept()
        t = threading.Thread(target=handle_client,args=(sock,""))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

