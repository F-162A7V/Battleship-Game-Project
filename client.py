__author__ = "F-162A7V"


import socket, pickle, pygame,struct,threading,os,tkinter,winclass
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


pause = False
aesobj = ""

#region Send/recieve
def makeSendableMsg(msg):
    try:
        msg = msg.encode()
    except:
        pass
    return struct.pack("I",len(msg)) + msg

def makeSendableMENC(msg):
    global aesobj
    try:
        msg = msg.encode()
    except:
        pass
    nonce = os.urandom(12)
    msg = aesobj.encrypt(nonce,msg,b"")
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
    return aesobj.decrypt(nonce, response[12:])
#endregion

#region Graphics - Entry
def Pick(sock):
    global current_window
    win = winclass.Window("LOGIN", "200x400")
    current_window = win
    sign = winclass.customButton(win, 25, "SIGNUP", command=lambda: signWin(sock, win), offset=(0, 20))
    log = winclass.customButton(win, 25, "LOGIN", command=lambda: logWin(sock, win), offset=(0, 30))
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
    send = winclass.customButton(win, 25, "Submit", command=lambda: signFunc(sock, namefield, passfield,emfield, win))
    win.root.mainloop()


def loginFunc(sock, namefield, passfield, parent=0):
    global aesobj
    if parent:
        parent.root.destroy()
    data = f"LOGN--||||--{namefield.text_var.get()}--||||--{passfield.text_var.get()}"
    sock.send(makeSendableMENC(data))
    resp = recieveENC(sock,aesobj)
    fields = resp.split(b'--||||--')
    if fields[0] == b"LOGR":
        mainGameWin(sock)
    elif fields[0] == b'EROR':
        pass


def signFunc(sock, namefield, passfield, email, parent=0):
    global aesobj
    if parent:
        parent.root.destroy()
    data = f"SIGN--||||--{email.text_var.get()}--||||--{namefield.text_var.get()}--||||--{passfield.text_var.get()}"
    sock.send(makeSendableMENC(data))
    resp = recieveENC(sock,aesobj)
    fields = resp.split(b'--||||--')
    if fields[0] == b"SIGR":
        mainGameWin(sock)
    elif fields[0] == b'EROR':
        pass


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
    global aesobj
    if parent:
        parent.root.destroy()
    if stage == 0:
        data = f"FGTP--||||--{textvar.text_var.get()}"
        sock.send(makeSendableMENC(data))
        resp = recieveENC(sock,aesobj)
        fields = resp.split(b'--||||--')
        if fields[0] == b"FGPR":
            forgotWin(sock,1,parent)
    elif stage == 1:
        data = f'FPCD--||||--{textvar.text_var.get()}'
        sock.send(makeSendableMENC(data))
        resp = recieveENC(sock,aesobj)
        fields = resp.split(b'--||||--')
        if fields[0] == b"FPCR":
            forgotWin(sock,2,parent)
    elif stage == 2:
        data = f'NEWP--||||--{textvar.text_var.get()}'
        sock.send(makeSendableMENC(data))
        resp = recieveENC(sock,aesobj)
        fields = resp.split(b'--||||--')
        if fields[0] == b"NEWR":
            print("Password changed successfully")
    return

#endregion

def mainGameWin(sock):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("DENMARK STRAIT")
    bg_img = pygame.image.load("assets/water2.jpg").convert()
    hood_img = pygame.image.load("assets/hoodplayer_2.png").convert_alpha()
    bismarck_img = pygame.image.load("assets/bismarckplayer_2.png").convert_alpha()
    while True:
        handlegameupdates(sock)

def handlegameupdates(sock,request=0):
    if request:
        msg = makeSendableMENC(request)
        sock.send(msg)


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
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1,
    )
    with open('public_key.pem', 'wb') as f:
        f.write(pem_public)

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
        return b'RSAdecFAIL'

def encrypt(sock):
    global aesobj
    private_key,public_key = load_keys()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1,)
    msg = b'HELO--||||--' + pem_public
    sock.send(makeSendableMsg(msg))
    resp = recieveData(sock)[0]
    decresp = RSAdec(resp,private_key)
    fields = decresp.split(b'--||||--')
    if fields[0] == b'AESK':
        AEkey = fields[1]
        aesobj = AESGCM(AEkey)
        mainpass(sock)
#endregion

def mainpass(sock):
    #Pick(sock)
    sock.send(makeSendableMENC("LOGR--||||--t1--||||--t1"))
    sock.send(makeSendableMENC("JOIN"))

def main():
    if not os.path.isfile("/private_key.pem") or not os.path.isfile("/public_key.pem"):
        GenRSAkeys()
    sock = socket.socket()
    while True:
        try:
            sock.connect(("127.0.0.1",11111))
            break
        except:
            print("Error connecting: server unavailable")
    encrypt(sock)


if __name__ == '__main__':
    main()

