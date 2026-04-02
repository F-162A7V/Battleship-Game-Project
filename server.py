__author__ = "F-162A7V"



import socket, pickle, threading,hashlib, struct,pygame,os,tkinter
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


stop = False

def makeSendableMsg(msg):
    try:
        msg = msg.encode()
    except:
        pass
    return struct.pack("I",len(msg)) + msg


def parse_msg(byteresp):



def handle_client(sock,notuple):



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

