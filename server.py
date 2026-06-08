__author__ = "F-162A7V"



import socket, pickle, threading, struct,pygame,os, senderobject, random, smtplib,ssl,time,traceback,sys, math

from dns.update import Update
from email_validator import validate_email
from email.message import EmailMessage
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import padding
from hashlib import sha256
from battleshiplayer import Player



users = {}
diction = senderobject.Sender()
pepper = "3BM-42_A:"
stop = False
queue = []
threads = []
lock = threading.Lock()


#region Send/recieve
def makeSendableMsg(msg):
    try:
        msg = msg.encode()
    except:
        pass
    return struct.pack("I",len(msg)) + msg

def makeSendableMENC(AESobj,msg):
    try:
        msg = msg.encode()
    except:
        pass
    nonce = os.urandom(12)
    msg = AESobj.encrypt(nonce,msg,b'')
    msg = nonce + msg
    return struct.pack("I",len(msg)) + msg

def recieveChunks(sock, length):
    data = b''
    while len(data) < length:
        newdata = sock.recv(length - len(data))
        if newdata == b'':
            return "e"
        data += newdata
    if (data == b''):
        return "e"
    return data

def recieveData(sock):
    L = recieveChunks(sock,4)
    L = struct.unpack("I",L)[0]
    response = recieveChunks(sock,L)
    return response, response.split(b"--||||--")

def recieveENC(sock,aesobj):
    L = recieveChunks(sock,4)
    L = struct.unpack("I",L)[0]
    response = recieveChunks(sock,L)
    nonce = response[:12]
    msg = aesobj.decrypt(nonce, response[12:],b"")
    return msg, msg.split(b'--||||--')
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
            data, fields = recieveENC(sock,aesobj)
            if fields[0] == b'FPCD':
                if fields[1].decode == code:
                    msg = makeSendableMENC(aesobj,'FPCR')
                    sock.send(msg)
                    data, fields2 = recieveENC(sock)
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

def parse_msg(data,sock,aesobj):
    global diction,pepper,users
    data = data.decode()
    fields = data.split('--||||--')
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
                msg = 'SIGR'
            else:
                msg = 'EROR--||||--004'

        if code == "LOGN":
            username = fields[1]
            noenc_password = fields[2]
            if username in users:
                password = noenc_password + users[username][2] + pepper
                enc = sha256(password.encode()).hexdigest()
                if users[username][0] == enc:
                    msg = "LOGR"
                else:
                    msg = "EROR--||||--002"
            else:
                msg = "EROR--||||--002"
        if code == "FGTP":
            passchangesequence(sock,fields[1],aesobj)
        else:
            try:
                msg = makeSendableMENC(aesobj,msg)
                sock.send(msg)
                return msg
            except Exception as e2:
                traceback.print_exc()
    except Exception as e:
        traceback.print_exc()

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

def encryptexchange(sock,notuple=0):
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
        sock.send(makeSendableMsg("EROR--||||--005"))
#endregion


def clipassenc(sock,aesobj):
    global queue,lock
    print(aesobj)
    stop = False
    while not stop:
        data = recieveENC(sock,aesobj)[0]
        msg = parse_msg(data,sock,aesobj)
        with lock:
            if data.split(b'--||||--')[0] in (b'SIGN',b'LOGN'):
                stop = True
    stop = False
    while not stop:
        data = recieveENC(sock,aesobj)[0]
        with lock:
            if data.split(b'--||||--')[0] in (b'JOIN'):
                stop = True
                queue.append((sock,aesobj))




#region Game handling
def recieveENC_game(sock, aesobj):
    try:
        L_bytes = recieveChunks(sock, 4)
        if not L_bytes:
            return None
        L = struct.unpack("I", L_bytes)[0]
        data = recieveChunks(sock, L)
        if not data or len(data) < 12:
            return None
        nonce = data[:12]
        return aesobj.decrypt(nonce, data[12:], b"")
    except:
        return None


def createSessions(threads,notuple):
    global queue, lock
    while True:
        time.sleep(1)
        lock.acquire()
        if len(queue) > 1:
            socks1 = queue[0][0]
            socks2 = queue[1][0]
            if checkconnection(socks1) and checkconnection(socks2):
                t = threading.Thread(target=manageNewSession,args=(socks1,socks2,queue[0][1],queue[1][1]))
                threads.append(t)
                for x in queue:
                    if x[0] == socks1:
                        queue.remove(x)
                for x in queue:
                    if x[0] == socks2:
                        queue.remove(x)
                t.start()
        lock.release()

def manageNewSession(s1,s2,s1aes,s2aes):
    global queue, lock
    starttime = time.perf_counter()
    s1.send(makeSendableMENC(s1aes,"STRT--||||--BISMARCK"))
    s2.send(makeSendableMENC(s2aes,"STRT--||||--HOOD"))
    #s1.setblocking(False)
    #s2.setblocking(False)
    p1 = Player(400, 500, 0, 0, 0)
    p2 = Player(600, 300, 0, 0, 1)
    while True:
        s1.settimeout(0.1)
        s2.settimeout(0.1)
        lock.acquire()
        msg1 = ''
        msg2 = ''
        try:
            msg1 = recieveENC(s1, s1aes)[0]
        except:
            pass
        try:
            msg2 = recieveENC(s2, s2aes)[0]
        except:
            pass
        if msg1:
            p1 = upd_game(msg1,p1)
        if msg2:
            p2 = upd_game(msg2,p2)
        p1.change_coords()
        p2.change_coords()
        game_obj = pickle.dumps((p1, p2))
        msg = b'GSTT--||||--' + game_obj
        s1.send(makeSendableMENC(s1aes,msg))
        s2.send(makeSendableMENC(s2aes,msg))
        elapsed = time.perf_counter() - starttime
        if elapsed < 1/30:
            time.sleep(1/30 - elapsed)
        starttime = time.perf_counter()
        lock.release()

def upd_game(msg, plr):
    fields = msg.split(b"--||||--")
    request = fields[0]
    if request == b"PORT":
        plr.turn(1, 1)
    if request == b"STRB":
        plr.turn(-1, 1)
    if request == b"INCS":
        plr.change_velocity(1, 0.05)
    if request == b"DECS":
        plr.change_velocity(-1, 0.05)
    return plr


def checkconnection(sock):
    global queue, lock
    try:
        sock.getpeername()
        return True
    except socket.error:
        for x in queue:
            if x[0] == sock:
                queue.remove(x)
                return False

#endregion

def mainLoop(ip="127.0.0.1",port=11111):
    global stop, users, queue, threads
    if os.path.isfile("users.pkl"):
        with open('users.pkl', 'rb') as file:
            users = pickle.load(file)
    else:
        diction.socksender = {}
    sock = socket.socket()
    sock.bind((ip,port))
    sock.listen(100000)
    threads = []
    gamethread = threading.Thread(target=createSessions,args=(threads,""))
    gamethread.start()
    threads.append(gamethread)
    while not stop:
        c,a = sock.accept()
        t = threading.Thread(target=encryptexchange,args=(c,""))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == '__main__':
    ip = "127.0.0.1"
    port = 11111
    if len(sys.argv) >= 2:
        ip = sys.argv[1]
    if len(sys.argv) >= 3:
        port = sys.argv[2]
    mainLoop(ip,port)

