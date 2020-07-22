import socket
from queue import Queue
import time
import threading

"""
ClientSocket = socket.socket()
host = '127.0.0.1'
port = 1233

print('Waiting for connection')
try:
    ClientSocket.connect((host, port))
except socket.error as e:
    print(str(e))

Response = ClientSocket.recv(1024)
while True:
    #Input = input('Say Something: ')
    #ClientSocket.send(str.encode(Input))
    Response = ClientSocket.recv(1024)
    print(Response.decode('utf-8'))

ClientSocket.close()

"""

host = '127.0.0.1'
port = 1233

class Client:
    def __init__(self, cname):
            #super(BrokerFirst, self).__init__(cname,**kwargs)
            self.q = Queue()
            self.name = cname
            self.ClientSocket = socket.socket()
            
    def connect(self, portI):
        #self.ClientSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        self.ClientSocket.connect((host, port + portI))
        
    def recv_messages(self):
        while True:
            #Input = input('Say Something: ')
            #ClientSocket.send(str.encode(Input))
            Response = self.ClientSocket.recv(1024)
            print("{} gets message {}".format(self.name, Response.decode('utf-8')))
            check = Response.decode('utf-8')
            #print(Response.decode('utf-8'))
            if check == "end":
                print("CLOSE SOCKET")
                self.ClientSocket.close()
                
numberOfClients = int(input("Enter total number of clients: "))

objs = list()
for i in range(numberOfClients):
    objs.append(Client("Client" + str(i)))

for i in range(numberOfClients):
    objs[i].connect(0)
    
"""      
C1 = Client("C1")
C1.connect(0)

C2 = Client("C2")
C2.connect(0)

C3 = Client("C3")
C3.connect(0)

C4 = Client("C4")
C4.connect(0)

C5 = Client("C5")
C5.connect(0)

print(C1)
print(C2)
print(C3)
print(C4)
print(C5)
"""
threads = []
for i in range(numberOfClients):
    t = threading.Thread(target=objs[i].recv_messages, args=[])
    threads.append(t)
    
"""
t1 = threading.Thread(target=C1.recv_messages, args=[])
t2 = threading.Thread(target=C2.recv_messages, args=[])
t3 = threading.Thread(target=C3.recv_messages, args=[])
t4 = threading.Thread(target=C4.recv_messages, args=[])
t5 = threading.Thread(target=C5.recv_messages, args=[])
"""

for i in range(numberOfClients):
    threads[i].start()
    time.sleep(.1)
    
"""

t1.start()
time.sleep(.1)
t2.start()
time.sleep(.1)
t3.start()
time.sleep(.1)
t4.start()
time.sleep(.1)
t5.start()
"""


"""
import socket
import time
import threading
import sys

ClientSocket = socket.socket()

def clientthread(conn):
    buffer=""
    while True:
        data = conn.recv(8192)
        buffer+=data
        print buffer
    #conn.sendall(reply)
    conn.close()

def main():
    try:
        host = '127.0.0.1'
        port = 1233
        tot_socket = 26
        list_sock = []
        for i in range(tot_socket):
            s = socket.socket()
            s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            s.bind((host, port+i))
            s.listen(10)
            list_sock.append(s)
            #print "[*] Server listening on %s %d" %(host, (port+i))

        while 1:
            for j in range(len(list_sock)):
                conn, addr = list_sock[j].accept()
                print '[*] Connected with ' + addr[0] + ':' + str(addr[1])
                start_new_thread(clientthread ,(conn,))
        s.close()

    except KeyboardInterrupt as msg:
        sys.exit(0)


if __name__ == "__main__":
    main()
"""
