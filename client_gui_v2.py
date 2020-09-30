from tkinter import *
from tkinter.font import *
import socket
import sys
import select
import errno
import sys

class App:
    def __init__(self):
        self.HEADER_LENGTH=10
        self.IP="127.0.0.1"
        self.PORT=1234
        self.startIPPort()

    def popup(self, title,_text,_fg="black"):
        toplevel = Toplevel()
        #Setting Size and prevent the window being resized
        toplevel.title(title)
        toplevel.resizable(width=False, height=False)
        helv24 = Font(family='Helvetica', size=20, weight='bold')
        label1=tkinter.Label(toplevel, text=_text,font=helv24, anchor="center",fg=_fg)
        ok=tkinter.Button(toplevel, text="Ok", command=toplevel.destroy)
        label1.pack()
        ok.pack()

    def startIPPort(self):
        def validatePort(char, entry_value):
            chars=entry_value[:-1] #Selects all the text in the textbox except the last character
            if not char.isdigit():
                """if entered char is not a digit return false"""
                return False
            else:
                return True

        def validateIP(char, entry_value):
            chars=entry_value[:-1] #Selects all the text in the textbox except the last character
            if (not char.isdigit() and not "." in char) or (chars.count(".")>2 and "." in char):
                """if entered char is not a digit or is not "." or is not "-" then return false.
                If the entered char is "." and there is already 2 or more "." in text, return false."""
                return False
            else:
                return True

        def getIPPort(entry_ip:Entry, entry_port:Entry, root:Tk):
            if entry_ip.get():
                self.IP=entry_ip.get()
            if entry_port.get():
                self.PORT=int(entry_port.get())
            else:
                self.PORT=0
            if self.IP!="":
                if self.attemptToConnectToServer():
                    root.destroy()
                    self.getUsername()

        root=Tk()
        root.title("Set IP Address and Port")
        root.resizable(width=False, height=False)

        vcmdPort = (root.register(validatePort), '%S', '%P')
        vcmdIp = (root.register(validateIP), '%S', '%P')
        
        label_ip=Label(root, text="IP Address")
        label_ip.grid(row=0)
        
        label_port=Label(root, text="Port")
        label_port.grid(row=1)

        entry_ip=Entry(root,width=50)
        entry_ip.grid(row=0,column=1)
        entry_ip.insert(END, self.IP)
        entry_ip.config(validate='key', validatecommand=vcmdIp)

        entry_port=Entry(root,width=50, validatecommand=vcmdPort, validate = 'key')
        entry_port.grid(row=1,column=1)
        entry_port.insert(END, str(self.PORT))

        button_send=Button(root, text="Enter", command=lambda: getIPPort(entry_ip, entry_port, root), width=20)
        button_send.grid(columnspan=2)

        root.mainloop()

    def attemptToConnectToServer(self)->bool:
        try:
            self.client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.IP, self.PORT))
            self.client_socket.setblocking(False)
            print(f"Connected to {self.IP}:{self.PORT}")
            return True
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno!=errno.EWOULDBLOCK:
                print('Reading Error', str(e))
                self.popup("ERROR", "Could not connect to server")
                return False

    def getUsername(self):
        def getUsername(entry_username:Entry, root:Tk):
            username=entry_username.get()
            if username!="":
                my_username=username
                root.destroy()
                self.setupSocket(my_username)

        root=Tk()
        root.title("Enter Username")
        root.resizable(width=False,height=False)

        label_username=Label(root, text="Username")
        label_username.grid(row=0)

        entry_username=Entry(root,width=50)
        entry_username.grid(row=0,column=1)

        button_send=Button(root, text="Enter", command=lambda: getUsername(entry_username, root), width=20)
        button_send.grid(columnspan=2)

        root.mainloop()
    
    def setupSocket(self, my_username):
        self.username=my_username.encode('utf-8')
        username_header=f"{len(self.username):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(username_header+self.username)
        self.startGUI()

    def sendMessage(self, text_message:Text):
        message=text_message.get("1.0", END).strip()
        if message:
            text_message.delete("1.0", END)
            message=message.encode('utf-8')
            message_header=f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
            self.client_socket.send(message_header+message)

    def startGUI(self):
        root=Tk()
        root.title(f"Client GUI {self.username.decode('utf-8')}")
        root.geometry('{}x{}'.format(480, 640))
        root.resizable(width=False, height=False)

        text_chat=Text(root, bg="grey43", height=30)
        text_chat.pack(pady=(0,10))
        text_chat.config(state=DISABLED)

        text_message=Text(root, bg="grey43", height=7)
        text_message.pack()

        button_send=Button(root, text="Send", width=480, height=3, command=lambda: self.sendMessage(text_message))
        button_send.pack()

        self.update_clock(root, text_chat)
        root.mainloop()

    def update_clock(self, root, text_chat):
        try:
            username_header=self.client_socket.recv(self.HEADER_LENGTH)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()

            username_length=int(username_header.decode('utf-8').strip())
            username=self.client_socket.recv(username_length).decode('utf-8')

            message_header=self.client_socket.recv(self.HEADER_LENGTH)
            message_length=int(message_header.decode('utf-8').strip())
            message=self.client_socket.recv(message_length).decode('utf-8')

            text_chat.config(state=NORMAL)
            text_chat.insert(END, f"{username} > {message}\n")
            text_chat.config(state=DISABLED)
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno!=errno.EWOULDBLOCK:
                print('Reading Error', str(e))
                sys.exit()
        except:
            pass
        root.after(50, lambda: self.update_clock(root, text_chat))

if __name__ == "__main__":
    app=App()