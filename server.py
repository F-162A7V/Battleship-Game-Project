__author__ = "F-162A7V"



import socket, pickle, threading,hashlib, struct,pygame,os,tkinter
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding




stop = False


#region Send/recieve
def makeSendableMsg(msg):
    try:
        msg = msg.encode()
    except:
        pass
    return struct.pack("I",len(msg)) + msg

def makeSendableMENC(AESobj,msg):
    nonce = os.urandom(12)
    msg = AESobj.encrypt(nonce,msg)
    msg = nonce + msg
    return struct.pack("I",len(msg)) + msg

def recieveData(sock):
    L = sock.recv(4)
    L = struct.unpack("I",L)[0]
    response = sock.recv(L)
    return response, response.split(b"--||||--")

def recieveENC(sock,aesobj):
    L = sock.recv(4)
    L = struct.unpack("I",L)[0]
    response = sock.recv(L)
    nonce = response[:12]
    return aesobj.decrypt(nonce, response[12:],b"")
#endregion

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
    aesobj = AESGCM(AEKey)
    if fields[0] == b'HELO':
        public_key = serialization.load_pem_public_key(fields[1])
        msg = b'AESK--||||--' + AEKey
        enc_msg = RSAenc(msg,public_key)
        sock.send(makeSendableMsg(enc_msg))
        clipassenc(sock,aesobj)
    else:
        sock.send(makeSendableMsg("EROR--||||--001"))
#endregion


def handle_client(sock,notuple):
    encryptexchange(sock)


def clipassenc(sock,aesobj):
    pass

def mainLoop(ip="127.0.0.1",port=11111):
    global stop
    sock = socket.socket()
    sock.bind((ip,port))
    sock.listen(100000)
    threads = []
    while not stop:
        c,a = sock.accept()
        t = threading.Thread(target=handle_client,args=(c,""))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == '__main__':
    mainLoop()

