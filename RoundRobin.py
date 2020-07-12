import socket
import os
import sys
from _thread import *
from queue import Queue
import time
import threading
from threading import Event, Lock
import string
#from random import randint
from random import *

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0

#clients = []
#clients_lock = threading.Lock()

random_flag = True

flag = 1
endMessage = False
emptyQueues = 0
event = Event()
mutex = Lock()

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))
    
print('Waiting for a Connection..')
ServerSocket.listen(2)

class Publisher():
    def __init__(self, cname):
        #super(BrokerFirst, self).__init__(cname,**kwargs)
        self.name = cname
        self.cnt = 0
        
    def generate_string(self, RecvBroker):
        global endMessage
        while self.cnt < 20:
            min_char = 8
            max_char = 12
            allchar = string.ascii_letters + string.digits
            data = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
            RecvBroker.q.put(data)
            self.cnt = self.cnt + 1
            time.sleep(.1)
        endMessage = True
        #print("VREME SLANJA JE {}".format(toc - tic))
        print("END MESSAGE SET TO TRUE")

class Broker():
    #constructor for first broker
    def __init__(self, cname):
        #super(BrokerFirst, self).__init__(cname,**kwargs)
        self.q = Queue()
        self.numberOfClients = 0
        self.name = ""
        self.visited = False
        self.neighbours = []   
        self.ThreadCount = 0
        self.messageCount = 0
        self.clientList = []
        #self.clients = set()
        
    def threaded_client(self):
        global emptyQueues
        global endMessage
        global random_flag
        #connection.send(str.encode('Welcome to the Server\n'))
        print("\nServer {}".format(self))
        #global clients
        #print("List size {}".format(len(clients)))
        #for c in clients:
        #while self.messageCount < self.numberOfClients:
        #for c in self.clientList:
            #print("Client: {}".format(c))
            #data = connection.recv(2048)
        print("Broker {} salje poruku".format(self))
        #data = input("Client enter message: ")
            #reply = 'Server Says: ' + data.decode('utf-8')
            #if not data:
            #    break
            #connection = self.q.get()
        print("VELICINA REDA U {} JE {}".format(self, self.q.qsize()))
        if self.q.empty() == True and endMessage == True:
            print("{} broker has empty queue".format(self))
            emptyQueues += 1
            return
        
        print("Duzina liste (broj klijenata) {}".format(len(self.clientList)))
        if(False == random_flag):
            for c in self.clientList:
                #data = input("Enter message for client: ")
                mutex.acquire()
                data = self.q.get()
                mutex.release()
                print("{} sending ---> {}".format(self, data))
                c.sendall(str.encode(data))
                time.sleep(.1)
        else:
            #choosing random broker
            random_broker = randint(0, 2)
            if(1 == random_broker):
                length = len(self.clientList)
                #choosing random client
                random_client = randint(0, length - 1)
                iter = 0

                for c in self.clientList:
                    #data = input("Enter message for client: ")
                    if iter == random_client:
                        print("********** SALJEM PORUKU **********")
                        mutex.acquire()
                        data = self.q.get()
                        mutex.release()
                        print("{} sending ---> {}".format(self, data))
                        c.sendall(str.encode(data))
                        time.sleep(.1)
                        break
                    iter += 1

        #connection.sendall(str.encode(data))
        #    self.messageCount += 1
            
        #self.messageCount = 0
            #c.sendall(str.encode(data))
            #self.messageCount += 1
            #self.numberOfClients -= 1
        #connection.close()
    def wait_for_conn(self):
        #global clients
        while self.ThreadCount < self.numberOfClients:
            Client, address = ServerSocket.accept()
            self.clientList += [Client]
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            #start_new_thread(self.threaded_client, args = [])#(Client, ))
            #threading.Thread(target=self.threaded_client).start()
            #print("CLIENT IS: {}".format(Client))
            #start_new_thread(self.threaded_client, ())
            self.ThreadCount += 1
            print('Thread Number: ' + str(self.ThreadCount))
        #ServerSocket.close()
        
    def close_connection(self):
        for c in self.clientList:
            #c.sendall(str.encode("end"))
            c.close()
        
    #method for moving messages that could not be sent from 
    #current to next broker           
    def ReadFromQueueSendToQueue(self, src, dst):
        while True:
            while self.q.empty() == False:
                #take message from queue and send it to next broker queue
                a = src.q.get()
                #print("PREPISUJEM {} iz {} u {}".format(a, src, dst))
                dst.q.put(a)
                #send.wait()
        
#graph       
class Graph:
    nodes = list()
    edges = list()

    #constructor
    def __init__(self):
        self.nodes = list()
        self.edges = list()

    #breadth first search algorithm
    def BFS(self, s):
        global flag
        print("BFS")
        #mark all the vertices as not visited
        for i in range(len(self.nodes)):
            self.nodes[i].visited = False
        
        #mark first node as visited - starting node
        s.visited = True

        #create a queue for BFS
        queue = list()

        #enqueue the first node
        queue.append(s)
        #do the message publishing for the first node
        if flag == 1:
            s.wait_for_conn()
            print("Sacekao sam konekcije")
        elif flag == 2:
            #for c in s.clientList:
            s.threaded_client()
        else:
            s.close_connection()
        #for c in clients:
        #    print("CHECK CLIENT {}".format(c))
        #    s.threaded_client(c)
        print("Poslao sam poruke")
        #s.messageCount = 0
        
        #go through the graph, until all the nodes are visited
        while len(queue) != 0:
            print("Usao u queue")
            #dequeue a vertex from queue and print it
            s = queue.pop()
            print("POP: {}".format(s))
                
            #get all the adjacent brokers of the dequeued broker s.
            #if adjacent broker has not been visited, mark it as visited
            #and enqueue it
            for broker in s.neighbours:
                print("Proveravam komsijske cvorove")
                if broker.visited == False:
                    print("Stavaljam u red {}".format(broker))
                    queue.append(broker)
                    #publish messages for current broker
                    if flag == 1:
                        print()
                        print("Waiting for conn")
                        broker.wait_for_conn()
                    elif flag == 2:
                        print()
                        print("Sending messages")
                        #for c in broker.clientList:
                        broker.threaded_client()
                    else:
                        broker.close_connection()
                    broker.visited = True           
       
                        
                    
#testing graph - 3 brokers added
def Get_Predefined_Dag():
    sub_count = 1
    nodes = 3
    adjacency = list()
    subscriber_list = list()

    G = Graph()
    
    #make broker instances
    B1 = Broker("Broker1")
    B2 = Broker("Broker2")
    B3 = Broker("Broker3")
    """
    B2 = BrokerOther("Broker2")
    B3 = BrokerOther("Broker3")
    """
    
    #add number of clients for each broker
    B1.numberOfClients = 1
    B2.numberOfClients = 2
    B3.numberOfClients = 2
    
    B1.neighbours.append(B2)
    B2.neighbours.append(B3)
    B3.neighbours.append(B1)
    
    #B1.wait_for_conn()
    
    #for c in clients:
    #    B1.threaded_client(c)
        
    print("NAPRAVIO SAM KLIJENTE")
    """
    B2.clientCounter = 3
    B3.clientCounter = 1
    
    #add neighbour brokers
    B1.add_neighbour_broker(B2)
    B2.add_neighbour_broker(B3)
    B3.add_neighbour_broker(B1)
    """
    #start the brokers
    
    """
    B2.runOther()
    time.sleep(.2)
    B3.runOther()
    time.sleep(.2)
    """
    
    G.nodes.append(B1)
    G.nodes.append(B2)
    G.nodes.append(B3)
    """
    G.nodes.append(B2)
    G.nodes.append(B3)
    """
    
    #testing queue
    B1.q.put("Message One")
    #B1.q.put("Message Two")
    #B1.q.put("Message Three")
    B2.q.put("Message Four")
    B2.q.put("Message Five")
    B3.q.put("Message Six")
    B3.q.put("Liman")
    
    #thread instances
    t1 = threading.Thread(target=B1.ReadFromQueueSendToQueue, args=[B1, B2])
    t2 = threading.Thread(target=B2.ReadFromQueueSendToQueue, args=[B2, B3])
    t3 = threading.Thread(target=B3.ReadFromQueueSendToQueue, args=[B3, B1])
    
    #start the threads
    t1.start()
    time.sleep(.2)
    t2.start()
    time.sleep(.2)
    t3.start()

    print("AAAAAAAAAAAA")
    # Append adjacencies
    for i in range(len(adjacency)):
        G.edges.append(adjacency[i])
    # Append subscribers
    #G.subscribers = {G.nodes[0]: [S1, S2], G.nodes[1]: [S3, S4, S5], G.nodes[2]: [S6]}

    return G
    
graph = Get_Predefined_Dag()
graph.BFS(graph.nodes[0])
print()
print()
print("Flag set")
print("DUZINA GRAFA {}".format(len(graph.nodes)))
flag = 2 
print("Broker 1")
for c in graph.nodes[0].clientList:
    print("Node 0 {}".format(c))
print("Broker 2")
for c in graph.nodes[1].clientList:
    print("Node 1 {}".format(c))
print("Broker 3")
for c in graph.nodes[2].clientList:
    print("Node 2 {}".format(c))

P1 = Publisher("Publisher")
    
t1 = threading.Thread(target=P1.generate_string, args=[graph.nodes[0]])
tic = time.perf_counter()
t1.start()

while True:
    graph.BFS(graph.nodes[0])
    if emptyQueues == len(graph.nodes):
        toc = time.perf_counter()
        break

print("CLOSING CONNECTION")
print("Elapsed time: {}".format(toc - tic))
flag = 3
#interate through the graph to close connections
print("Closing connections")
#graph.BFS(graph.nodes[0]) 
ServerSocket.close()
#print("Exit program")
sys.exit()
