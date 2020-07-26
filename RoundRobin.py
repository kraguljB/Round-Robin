import socket
import os
import sys
from _thread import *
from queue import Queue
import time
import threading
from threading import Event, Lock
import string
from random import *

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0

#clients = []
#clients_lock = threading.Lock()

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
        self.clientNames = []
        #self.clients = set()
        
    def threaded_client(self):
        global emptyQueues
        global endMessage
        #connection.send(str.encode('Welcome to the Server\n'))
        print("Broker {} salje poruku".format(self))
        print("VELICINA REDA U {} JE {}".format(self, self.q.qsize()))
        
        print("Duzina liste {}".format(len(self.clientList)))
        for c in self.clientList:
            #data = input("Enter message for client: ")
            mutex.acquire()
            data = self.q.get()
            mutex.release()
            print("{} sending {}".format(self, data))
            c.sendall(str.encode(data))
            time.sleep(.1)
            if self.q.empty() == True:
                break
            
        if self.q.empty() == True and endMessage == True:
            print("{} broker has empty queue".format(self))
            emptyQueues += 1
            return
        
    def start_message_exchange(self):
        #send message from current broker to its neighbour broker
        t = threading.Thread(target=self.ReadFromQueueSendToQueue, args=[self, self.neighbours[0]])
        t.start()
        time.sleep(.1)
        
    def wait_for_conn(self):
        #global clients
        while self.ThreadCount < self.numberOfClients:
            Client, address = ServerSocket.accept()
            self.clientList += [Client]
            print('Connected to: ' + address[0] + ':' + str(address[1]))
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
            s.start_message_exchange()
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
                        broker.start_message_exchange()
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
    clientCount = 0
    nodes = int(input("Enter total number of nodes in graph: "))
    adjacency = list()

    G = Graph()
    
    #make broker instances
    objs = []
    for i in range(nodes):
        print("GARI PRAVIM BROKERE")
        objs.append(Broker("Broker" + str(i)))
        print("GARI BROKER: {}".format(objs[i]))
        print("IME BROKERA: {}".format(objs[i].name))
        
    for i in range(nodes):
        print("STAMPAM IMENA: {}".format(objs[i]))
    
    for i in range(nodes):
        numberOfClients = int(input("Enter total number of clients for Broker{}: ".format(i+1)))
        objs[i].numberOfClients = numberOfClients
        print("BROKER {} IMA {} KLIJENATA: ".format(objs[i], objs[i].numberOfClients))
        for j in range(objs[i].numberOfClients):
            objs[i].clientNames.append("Client" + str(clientCount))
            clientCount += 1
            print("CLIENT COUNT {}".format(clientCount))
    
    #add number of clients for each broker
    
    for i in range(nodes - 1):
        objs[i].neighbours.append(objs[i+1])
    
    objs[nodes - 1].neighbours.append(objs[0])
    
    for i in range(nodes):
        print("BROKER: {}".format(objs[i].name))
        G.nodes.append(objs[i])
    
    #B1.wait_for_conn()
    
    #for c in clients:
    #    B1.threaded_client(c)
        
    print("NAPRAVIO SAM KLIJENTE")
    
    #testing queue
    objs[0].q.put("Message One")
    objs[0].q.put("Message Four")
    objs[0].q.put("Message Five")
    objs[0].q.put("Message Six")
    objs[0].q.put("Liman")
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
"""
for c in graph.nodes[0].clientList:
    print("Node 0 {}".format(c))
    
for c in graph.nodes[1].clientList:
    print("Node 1 {}".format(c))
"""   
P1 = Publisher("Publisher")
    
t1 = threading.Thread(target=P1.generate_string, args=[graph.nodes[0]])
tic = time.perf_counter()
t1.start()

while True:
    graph.BFS(graph.nodes[0])
    if emptyQueues == len(graph.nodes):
        print("USAO SAM NA KRAJ")
        toc = time.perf_counter()
        break

print("CLOSING CONNECTION")
CPU_Pct=str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
#print results
print("CPU Usage = " + CPU_Pct)
print("Elapsed time: {}".format(toc - tic))
flag = 3
#interate through the graph to close connections
print("Closing connections")
#graph.BFS(graph.nodes[0]) 
ServerSocket.close()
#print("Exit program")
sys.exit()
