import socket
import threading

PORT = 5000
HOST = "0.0.0.0"

server = socket.socket()

server.bind((HOST, PORT))

server.listen(5)

offers = {}
client = {}
speakingTo = {}

def toS(byte):
    return byte.decode('utf-8')

def start():
    while(True):
        conn, addr = server.accept()
        print(conn, addr)
        creds = conn.recv(1024)
        creds = toS(creds)
        username, contact, mode = list(map(str, creds.split(';')))
        if mode == "make":
            if contact in offers:
                message = "User is in another call"
            else:
                offers[username] = contact
                client[username] = conn
                speakingTo[username] = contact
                message = "Your call has successfully been placed"
        else:
            if contact not in offers:
                message = "User you are looking for is not online"
            elif offers[contact] != username:
                message = "User is on another call"
            else:
                client[username] = conn
                speakingTo[username] = contact
                offers.pop(contact)
                message = "Your call has been connected successfully"
        print(message)
        client[username].send(message)

        t = threading.Thread(target = send, args = (username, ))
        t.start()

def send(username):
    try:
        while(True):
            data = client[username].recv(4096)
            client[speakinTo[username]].send(data)
    except:
        for user in client:
            try:
                message = "Call Disconnected"
                client[username].send(toB(message))
            except:
                pass

start()
