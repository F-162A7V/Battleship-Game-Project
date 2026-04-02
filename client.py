__author__ = "F-162A7V"


import socket, pickle, pygame,struct,threading,os,tkinter,winclass
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding



pause = False



def makeSendableMsg(msg):
    try:
        msg = msg.encode()
    except:
        pass
    return struct.pack("I",len(msg)) + msg

def recieveData(sock):
    L = sock.recv(4)
    L = struct.unpack("I",L)[0]
    response = sock.recv(L)
    return response, response.split(b"--||||--")

def recieveENC(sock):
    L = sock.recv(4)
    L = struct.unpack("I",L)[0]
    response = sock.recv(L)
    return response


#region Graphics - Entry
def Pick(sock):
    global current_window
    win = winclass.Window("LOGIN", "200x400")
    current_window = win
    sign = winclass.customButton(win, 25, "LOGIN", command=lambda: signWin(sock, win), offset=(0, 20))
    log = winclass.customButton(win, 25, "SIGNUP", command=lambda: logWin(sock, win), offset=(0, 30))
    forgt = winclass.customButton(win, 25, "FORGOT PASS", command=lambda: forgotWin(sock,0, win), offset=(0, 40))
    win.root.mainloop()

def logWin(sock, parent=0):
    global current_window
    if parent:
        parent.root.destroy()
    win = winclass.Window("LOGIN","200x300")
    current_window = win
    namefield = winclass.customEntry(win, 25, 25, lbl="Enter User:")
    passfield = winclass.customEntry(win, 25, 25, (0, 25), "*", lbl="Enter Password:")
    send = winclass.customButton(win, 25, "Submit", command=lambda: loginFunc(sock, namefield, passfield, win),
                                 offset=(0, 40))
    win.root.mainloop()

def signWin(sock, parent=0):
    global current_window
    if parent:
        parent.root.destroy()
    win = winclass.Window("SIGNUP", "200x300")
    current_window = win
    namefield = winclass.customEntry(win, 25, 25, lbl="Enter Email:")
    emfield = winclass.customEntry(win, 25, 25, lbl="Enter Username:")
    passfield = winclass.customEntry(win, 25, 25, (0, 25), "*", lbl="Enter Password:")
    send = winclass.customButton(win, 25, "Submit", command=lambda: signFunc(sock, namefield, passfield,emfield, win),offset=(0, 40))
    win.root.mainloop()


def loginFunc(sock, namefield, passfield, parent=0):
    data = f"LOGN|``|{namefield.text_var.get()}|``|{passfield.text_var.get()}"
    sock.send(makeSendableMsg(data))
    resp = recieveData(sock)
    fields = resp.split(b'|``|')
    if fields[0] == b"LOGR":
        mainGameWin(sock)
    elif fields[0] == b'EROR':
        pass
    if parent:
        parent.root.destroy()

def signFunc(sock, namefield, passfield, email, parent=0):
    data = f"LOGN|``|{email}|``|{namefield.text_var.get()}|``|{passfield.text_var.get()}"
    sock.send(makeSendableMsg(data))
    resp = recieveData(sock)
    fields = resp.split(b'|``|')
    if fields[0] == b"SIGR":
        mainGameWin(sock)
    elif fields[0] == b'EROR':
        pass
    if parent:
        parent.root.destroy()


def forgotWin(sock, stage,parent=0):
    global current_window
    if parent:
        parent.root.destroy()
    if stage == 0:
        win = winclass.Window("FORGOT PASS", "200x300")
        current_window = win
        emfield = winclass.customEntry(win, 25, 25, lbl="Enter Email:")
        send = winclass.customButton(win, 25, "Submit", command=lambda: forgotFunc(sock, emfield,0, win), offset=(0, 40))
    elif stage == 1:
        win = winclass.Window("ENTER CODE", "200x300")
        codefield = winclass.customEntry(win, 25, 25, (0, 25), lbl="ENTER EMAIL CODE:")
        send = winclass.customButton(win, 25, "Submit", command=lambda: forgotFunc(sock, codefield,1, win),offset=(0, 40))
    elif stage == 2:
        win = winclass.Window("ENTER NEW PASSWORD", "200x300")
        newpassfield = winclass.customEntry(win, 25, 25, (0, 25), shw="*", lbl="ENTER NEW PASSWORD:")
        send = winclass.customButton(win, 25, "Submit", command=lambda: forgotFunc(sock, newpassfield,2, win),offset=(0, 40))
    win.root.mainloop()


def forgotFunc(sock, textvar, stage, parent=0):
    if stage == 0:
        data = f"FGTP|``|{textvar.text_var.get()}"
        sock.send(makeSendableMsg(data))
        resp = recieveData(sock)
        fields = resp.split(b'|``|')
        if fields[0] == b"FGPR":
            forgotWin(sock,1,parent)
    elif stage == 1:
        data = f'FPCD|``|{textvar.text_var.get()}'
        sock.send(makeSendableMsg(data))
        resp = recieveData(sock)
        fields = resp.split(b'|``|')
        if fields[0] == b"FPCR":
            forgotWin(sock,2,parent)
    elif stage == 2:
        data = f'NEWP|``|{textvar.text_var.get()}'
        sock.send(makeSendableMsg(data))
        resp = recieveData(sock)
        fields = resp.split(b'|``|')
        if fields[0] == b"NEWR":
            print("Password changed successfully")
    return

#endregion

def mainGameWin(sock):
    return

#region Encryption
def GenRSAkeys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b'mypassword')
    )
    with open('private_key.pem', 'wb') as f:
        f.write(pem_private)
    public_key = private_key.public_key()
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(b'mypassword')
    )
    with open('private_key.pem', 'wb') as f:
        f.write(pem_private)

def load_keys():
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=b'mypassword',
            backend=default_backend()
    )

    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )
    return private_key, public_key

def RSAdec(encrypted_message,private_key):
    try:
        message = private_key.decrypt(
            encrypted_message,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return message
    except ValueError:
        return "Decryption failed: Key incorrect"

def encrypt(sock):
    private_key,public_key = load_keys()
    msg = b'HELO--||||--' + pickle.dumps(public_key)
    sock.send(makeSendableMsg(msg))
    resp = recieveENC(sock)
    decresp = RSAdec(resp,private_key)
    fields = decresp.split(b'--||||--')
    if fields[0] == b'AESK':
        AESobject = pickle.loads(fields[1])
        



#endregion

def main():
    if not os.path.isfile("/private_key.pem"):
        GenRSAkeys()
