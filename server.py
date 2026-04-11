__author__ = "F-162A7V"



import socket, pickle, threading, struct,pygame,os, senderobject, random, smtplib,ssl,time
from email_validator import validate_email
from email.message import EmailMessage
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from hashlib import sha256



users = {}
diction = senderobject.Sender()
pepper = "3BM-42_A:"
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

#region loginhandle
def hash_pass(password,salt):
    global pepper
    password = password + salt + pepper
    return sha256(password.encode()).hexdigest()

def send_email(email_reciever,email_subject,email_body):
    email_sender = "yoavsarig4@gmail.com"
    email_password = 'rceb pwyw jfey ccrh'
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_reciever
    em['Subject'] = email_subject
    em.set_content()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_reciever,em.as_string())

def findUsernameByEmail(email):
    global users
    for key in users:
        if users[key][1] == email:
            return key
    return "-1"

def ResetCodeTimer(username,notuple):
    global users, stop
    t1 = time.perf_counter()
    while not stop:
        t2 = time.perf_counter()
        if t2 - t1 > 300:
            users[username][3] = False

def passchangesequence(sock,tgtemail,aesobj):
    global users, pepper, threads
    tgt_user = findUsernameByEmail(tgtemail)
    try:
        if validate_email(tgtemail) and users[tgt_user][1].decode() == tgtemail:
            msg = "FGTR"
            msg = makeSendableMENC(aesobj,msg)
            code = str(random.randint(1,999999)).zfill(6)
            send_email(tgtemail,"AsyncServerGui password reset code:", code)
            sock.send(msg)
            tn = threading.Thread(target=ResetCodeTimer,args=(tgt_user,""))
            tn.start()
            threads.append(tn)
            users[tgt_user][3] = True
            data, fields = recieveData(sock)
            if fields[0] == b'FPCD':
                if fields[1].decode == code:
                    msg = makeSendableMENC(aesobj,'FPCR')
                    sock.send(msg)
                    data, fields2 = recieveData(sock)
                    if fields2[0] == 'NEWP':
                        new_pass = fields2[1]
                        salt = users[tgt_user][2]
                        users[tgt_user][0] = hash_pass(new_pass,salt)
                        msg = makeSendableMENC(aesobj,'NEWR')
                    else:
                        msg = makeSendableMENC(aesobj,"EROR|005")
                        sock.send(msg)
                else:
                    msg = makeSendableMENC(aesobj,'EROR|008')
                    sock.send(msg)
            else:
                msg = makeSendableMENC(aesobj,'EROR|005')
                sock.send(msg)
        else:
           sock.send(makeSendableMENC(aesobj,'EROR|009'))
    except:
        pass
#endregion


def parse_msg(fields,sock):
    global diction
    global pepper
    try:
        code = fields[0]
        msg = ''
        if code == 'SIGN':
            email = fields[1]
            username = fields[2]
            noenc_password = fields[3]
            if username not in users:
                salt = sha256(str(random.randint(0,10000000)).encode()).hexdigest()[:6]
                password = noenc_password + salt + pepper
                login_underway = False
                users[username] = [sha256(password.encode()).hexdigest(),email,salt,login_underway]
                diction.socksender[username] = []
                with open("users.pkl", "wb") as fil:
                    pickle.dump(users, fil)
                msg = 'SIGR|``|T'
            else:
                msg = 'EROR|``|004'

        if code == "LOGN":
            username = fields[1]
            noenc_password = fields[2]
            if username in users:
                password = noenc_password + users[username][2] + pepper
                enc = sha256(password.encode()).hexdigest()
                if users[username][0] == enc:
                        msg = "LOGR"
                else:
                    msg = "EROR|``|002"
            else:
                msg = "EROR|``|002"

        if code == "FGTP":
            passchangesequence(sock,fields[1])
        if code == "MESG":
            keys = diction.socksender.keys()
            if fields[2] in keys:
                msg = f'MESS|``|{fields[1]}|``|{fields[3]}'
            else:
                msg = "EROR|``|003"
    except IndexError:
        msg = "EROR|``|005"
    length = struct.pack("I",len(msg))
    msg = length + msg.encode()
    if msg[:4] == "MESS":
        print(msg)
        diction.AddMsg(fields[2],msg)
        with open("messages.pkl", "wb") as fil:
            pickle.dump(diction.socksender, fil)
    else:
        try:
            print(msg)
            sock.send(msg)
        except:
            pass


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
    with open('users.pkl', 'rb') as file:
        users = pickle.load(file)
    with open('messages.pkl','rb') as file:
        diction.socksender = pickle.load(file)
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

