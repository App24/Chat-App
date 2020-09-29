from tkinter import *
import socket
import sys
import select
import errno
import sys

HEADER_LENGTH=10
IP="127.0.0.1"
PORT=1234
my_username=""

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

def getIPPort(ipText:Text, portText:Text, root:Tk):
    global IP, PORT
    if ipText.get():
        IP=ipText.get()
    if portText.get():
        PORT=int(portText.get())
    else:
        PORT=0
    if IP!="":
        root.destroy()

root=Tk()
root.resizable(width=False, height=False)

vcmdPort = (root.register(validatePort), '%S', '%P')
vcmdIp = (root.register(validateIP), '%S', '%P')

ipText=Entry(root, bg="cyan",width=50)
ipText.pack()
ipText.insert(END, IP)
ipText.config(validate='key', validatecommand=vcmdIp)

portText=Entry(root, bg="cyan",width=50, validatecommand=vcmdPort, validate = 'key')
portText.pack()
portText.insert(END, str(1234))

sendButton=Button(root, text="Enter", command=lambda: getIPPort(ipText, portText, root), width=50)
sendButton.pack()

root.mainloop()

def getUsername(usernameText:Text, root:Tk):
    global my_username
    username=usernameText.get("1.0", END).strip()
    if username!="":
        my_username=username
        root.destroy()

root=Tk()
root.resizable(width=False,height=False)

ipText=Text(root, bg="cyan", height=1,width=50)
ipText.pack()

sendButton=Button(root, text="Enter", command=lambda: getUsername(ipText, root), width=50)
sendButton.pack()

root.mainloop()

if my_username=="": 
    sys.exit()

client_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

username=my_username.encode('utf-8')
username_header=f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header+username)

def sendMessage(messageText:Text):
    message=messageText.get("1.0", END).strip()
    if message:
        messageText.delete("1.0", END)
        message=message
        message=message.encode('utf-8')
        message_header=f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header+message)

def update_clock(root, chatText):
    try:
        username_header=client_socket.recv(HEADER_LENGTH)
        if not len(username_header):
            print("Connection closed by the server")
            sys.exit()

        username_length=int(username_header.decode('utf-8').strip())
        username=client_socket.recv(username_length).decode('utf-8')

        message_header=client_socket.recv(HEADER_LENGTH)
        message_length=int(message_header.decode('utf-8').strip())
        message=client_socket.recv(message_length).decode('utf-8')

        chatText.config(state=NORMAL)
        chatText.insert(END, f"{username} > {message}\n")
        chatText.config(state=DISABLED)
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno!=errno.EWOULDBLOCK:
            print('Reading Error', str(e))
            sys.exit()
    except:
        pass
    root.after(50, lambda: update_clock(root, chatText))

root=Tk()
root.title(f"Client GUI {username.decode('utf-8')}")
root.geometry('{}x{}'.format(480, 640))
root.resizable(width=False, height=False)

chatText=Text(root, bg="red", height=30)
chatText.pack()
chatText.config(state=DISABLED)

messageText=Text(root, bg="cyan", height=7)
messageText.pack()

sendButton=Button(root, text="Send", width=480, height=3, command=lambda: sendMessage(messageText))
sendButton.pack()

update_clock(root, chatText)
root.mainloop()
