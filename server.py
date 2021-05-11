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
                client[username] = conn
            else:
                offers[username] = contact
                client[username] = conn
                speakingTo[username] = contact
                message = "Your call has successfully been placed"
        else:
            if contact not in offers:
                message = "User you are looking for is not online"
                client[username] = conn
            elif offers[contact] != username:
                message = "User is on another call"
                client[username] = conn
            else:
                client[username] = conn
                speakingTo[username] = contact
                offers.pop(contact)
                message = "Your call has been connected successfully"
        print(message)
        message = message.encode('utf-8')
        client[username].send(message)

        t = threading.Thread(target = send, args = (username, ))
        t.start()

def send(username):
    print(client, speakingTo, offers, sep = "\n")
    try:
        while(True):
            print(username + " sending to " + speakingTo[username])
            data = client[username].recv(4096)
            print("recieved from " + username)
            client[speakinTo[username]].send(data)
            print("sent to " + speakingTo[username])
    except:
        for user in client:
            try:
                message = "Call Disconnected"
                message = message.encode('utf-8')
                client[username].send(message)
            except:
                pass

start()
