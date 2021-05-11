import socket
import threading
import pyaudio
import tkinter as tk

def toS(byte):
    return byte.decode('utf-8')

class callingInterface:
    def __init__(self):
        self.client = socket.socket()
        # self.HOST = "127.0.0.1"
        self.HOST = "65.1.163.34"
        self.PORT = 5000
        self.client.connect((self.HOST, self.PORT))
        self.p = pyaudio.PyAudio()

        self.input_stream = self.p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = 4096)
        self.output_stream = self.p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, output = True, frames_per_buffer = 4096)

    def sendCreds(self, username, contact, mode):
        data = [username, contact, mode]
        data = ';'.join(data)
        self.client.send(bytes(data, 'utf-8'))
    
    def sendStream(self):
        while(True):
            try:
                data = self.input_stream.read(4096)
                self.client.send(data)
            except:
                break

    def receiveStream(self, miniDisplay):
        while(True):
            try:
                data = self.client.recv(4096)
                miniDisplay.insert(tk.END, repr(data))
                miniDisplay.insert(tk.END, '\n')
                self.output_stream.write(data)
            except:
                break

    def startCall(self, miniDisplay):
        miniDisplay.insert(tk.END, "Credentials relayed to the server...\n")
        miniDisplay.insert(tk.END, "Please wait, your call will begin...\n")
        message = self.client.recv(1024)
        message = toS(message)

        miniDisplay.insert(tk.END, message)
        miniDisplay.insert(tk.END, '\n')

        t1 = threading.Thread(target = sendStream)
        t2 = threading.Thread(target = receiveStream, args = (miniDisplay, ))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    def endCall(self):
        self.input_stream.stop()
        self.input_stream.close()
        self.output_stream.stop()
        self.output_stream.close()

caller = callingInterface()

class page(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for f in (homePage, callPage):
            frame = f(container, self)
            self.frames[f] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(homePage)

    def show_frame(self, cont):
        if cont == homePage:
            self.title("Walkie-Talkie Homepage")
        else:
            self.title("Walkie-Talkie Calling Interface")
        frame = self.frames[cont]
        frame.tkraise()

class homePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        label_username = tk.Label(self, text="Username")
        label_contact = tk.Label(self, text="Contact")

        entry_username = tk.Entry(self)
        entry_contact = tk.Entry(self)

        label_username.grid(row=1, column=0, padx=10,pady=10)
        label_contact.grid(row=2, column=0, padx=10,pady=10)
        entry_username.grid(row=1, column=1, padx=10,pady=10)
        entry_contact.grid(row=2, column=1, padx=10,pady=10)

        makeCallBtn = tk.Button(self, text="Make a call", width=10, background="white", foreground="Black",command=lambda: makeCallBtn_clicked())
        makeCallBtn.grid(row=5, column=0, columnspan = 2, padx=10, pady=10)

        connectCallBtn = tk.Button(self, text="Connect to call", width=10, background="white", foreground="Black",command=lambda: connectCallBtn_clicked())
        connectCallBtn.grid(row=6, column=0, columnspan = 2, padx=10, pady=10)

        def makeCallBtn_clicked():
            username = entry_username.get()
            contact = entry_contact.get()
            caller.sendCreds(username, contact, "make")
            controller.show_frame(callPage)

        def connectCallBtn_clicked():
            username = entry_username.get()
            contact = entry_contact.get()
            caller.sendCreds(username, contact, "connect")
            controller.show_frame(callPage)

class callPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        message_label=tk.Label(self,text="Status",font=("Arial,12"))
        message_label.grid(row=1,column=0,columnspan=3,padx=10,pady=10,sticky="NSEW")

        scrollbar_y = tk.Scrollbar(self)
        scrollbar_y.grid(row=4, column=3,rowspan=6)

        miniDisplay = tk.Text(self,height=8, width=35, yscrollcommand=scrollbar_y.set,
                       bg="Grey",fg="White")
        miniDisplay.grid(row=4, column=0,rowspan=3,columnspan=3,sticky="NSEW")

        # caller.startCall(miniDisplay)
        startCallBtn = tk.Button(self,text="Start call",width = 10,command=lambda: startCallBtn_clicked())
        startCallBtn.grid(row=14,column=0,padx=10,pady=10,sticky="nsew")

        endCallBtn = tk.Button(self,text="End call",width = 10, command=lambda: endCallBtn_clicked())
        endCallBtn.grid(row=14,column=1,padx=10,pady=10,sticky="nsew")
        
        def startCallBtn_clicked():
            caller.startCall(miniDisplay)
        def endCallBtn_clicked():
            caller.endCall()
            controller.show_frame(homePage)

app = page()
app.mainloop()