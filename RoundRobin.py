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
import psutil

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
totalMessagesSentCount = 0

#clients = []
#clients_lock = threading.Lock()

random_flag = False
sticky_flag = False

flag = 1
available = True
endMessage = False
emptyQueues = 0
event = Event()
mutex = Lock()

#fix [Errno 98]
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))
    
print('Waiting for a Connection..')
ServerSocket.listen(2)

def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

cpufreq = psutil.cpu_freq()
print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
print(f"Current Frequency: {cpufreq.current:.2f}Mhz")

print("CPU Usage Per Core:")
for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
    print(f"Core {i}: {percentage}%")
print(f"Total CPU Usage: {psutil.cpu_percent()}%")

class Publisher():
    def __init__(self, cname):
        #super(BrokerFirst, self).__init__(cname,**kwargs)
        self.name = cname
        self.cnt = 0
        self.end = False
        
    def generate_string(self, RecvBroker):
        global endMessage
        min_char = 8
        max_char = 12
        while self.cnt < 95:
            allchar = string.ascii_letters + string.digits
            data = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
            if RecvBroker.q.qsize() < RecvBroker.numberOfClients:
                RecvBroker.q.put(data)
            else:
                RecvBroker.q2.put(data)
            self.cnt = self.cnt + 1
            #time.sleep(.1)
        endMessage = True
        self.end = True
        #print("VREME SLANJA JE {}".format(toc - tic))
        print("END MESSAGE SET TO TRUE")

class Broker():
    #constructor for first broker
    def __init__(self, cname):
        #super(BrokerFirst, self).__init__(cname,**kwargs)
        self.q = Queue()
        self.q2 = Queue()
        self.numberOfClients = 0
        self.name = ""
        self.visited = False
        self.neighbours = []   
        self.ThreadCount = 0
        self.messageCount = 0
        self.clientList = []
        self.clientNames = []
        
    def threaded_client(self):
        global emptyQueues
        global endMessage
        global totalMessagesSentCount
        global random_flag
        global sticky_flag
        #connection.send(str.encode('Welcome to the Server\n'))
        print("Broker {} salje poruku".format(self))
        print("VELICINA REDA U {} JE {}".format(self, self.q.qsize()))
        print("VELICINA REDA2 U {} JE {}".format(self, self.q2.qsize()))
        #event.set()
        
        if self.q.empty() == True and endMessage == True:
            print("{} broker has empty queue".format(self))
            emptyQueues += 1
            return

        print("Duzina liste {}".format(len(self.clientList)))

        #roundRobin
        if(False == random_flag and False == sticky_flag):
            print("\n ROUND ROBIN")

            for c in self.clientList:
                #data = input("Enter message for client: ")
                #print("GARISA")
                print("********** SALJEM PORUKU - RR **********")
                if self.q.empty() == True and self.q.empty() == True:
                    event.set()
                    return
                mutex.acquire()
                data = self.q.get()
                mutex.release()
                print("{} sending {}".format(self, data))
                c.sendall(str.encode(data))
                totalMessagesSentCount += 1
                if totalMessagesSentCount == 100:
                    event.set()
                    return
                time.sleep(.1)
            event.set()
        #sticky
        elif(False == random_flag and True == sticky_flag):
            print("\n STICKY")
            #this number represents how many times certain client will be targeted
            #repeat_client = 0
            """
            for c in self.clientList:
                repeat_client = randint(1, 4)
                mutex.acquire()
                data = self.q.get()
                mutex.release()
                for iter in range(0, repeat_client):
                    print("{} sending ---> {}".format(self, data))
                    c.sendall(str.encode(data))
                    time.sleep(.1)
                    """
            #choosing random broker (sticky is in fact random algorith which targets same client multiple times)
            random_broker = randint(0, 2)
            if(1 == random_broker):
                length = len(self.clientList)
                #choosing random client
                random_client = randint(0, length - 1)
                iter = 0
                #this number represents how many times certain client will be targeted
                #repeat_client = 0

                for c in self.clientList:
                    #data = input("Enter message for client: ")
                    if iter == random_client:
                        #repeat_client = randint(1, 10)
                        print("********** SALJEM PORUKU - sticky **********")
                        mutex.acquire()
                        data = self.q.get()
                        mutex.release()
                        #for same_client_iter in range(0, repeat_client):
                        while(True):
                            print("{} sending ---> {}".format(self, data))
                            c.sendall(str.encode(data))
                            time.sleep(.1)
                        break
                    iter += 1

                for c in self.clientList:
                    #data = input("Enter message for client: ")
                    if iter == random_client:
                        #print("GARISA")
                        if self.q.empty() == True and self.q.empty() == True:
                            event.set()
                            return
                        repeat_client = randint(1, 10)
                        print("********** SALJEM PORUKU **********")
                        mutex.acquire()
                        data = self.q.get()
                        mutex.release()
                        for same_client_iter in range(0, repeat_client):
                            print("{} sending {}".format(self, data))
                            c.sendall(str.encode(data))
                            totalMessagesSentCount += 1
                            if totalMessagesSentCount == 100:
                                event.set()
                                return
                            time.sleep(.1)
                        break
                event.set()
        #random
        elif(True == random_flag and False == sticky_flag):
            print("\n RANDOM")
            #choosing random broker
            random_broker = randint(0, 2)
            if(1 == random_broker):
                length = len(self.clientList)
                #choosing random client
                random_client = randint(0, length - 1)
                iter = 0

                for c in self.clientList:
                    #data = input("Enter message for client: ")
                    #print("GARISA")
                    print("********** SALJEM PORUKU - random **********")
                    if self.q.empty() == True and self.q.empty() == True:
                        event.set()
                        return
                    mutex.acquire()
                    data = self.q.get()
                    mutex.release()
                    print("{} sending {}".format(self, data))
                    c.sendall(str.encode(data))
                    totalMessagesSentCount += 1
                    if totalMessagesSentCount == 100:
                        event.set()
                        return
                    time.sleep(.1)
                event.set()
        else:
            print("\n\n SOMETHING WENT WRONG! PLEASE CHECK YOUR GLOBAL ALGORITHM FLAGS! \n\n")
            sys.exit()
 
    def start_message_exchange(self):
        #send message from current broker to its neighbour broker
        print("POKRECEM START MESSAGE EXCHANGE ZA {}".format(self))
        t = threading.Thread(target=self.ReadFromQueueSendToQueue, args=[self, self.neighbours[0]])
        t.start()
        time.sleep(.1)
    
    """
    def start_queue_exchange(self):
        t = threading.Thread(target=self.read_from_broker_queue, args=[])
        t.start()
        time.sleep(.1)
    """
        
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
        global endMessage
        while True:
            event.wait()
            while src.q2.empty() == False:
                #print("GARIIIIIIII")
                #take message from queue and send it to next broker queue
                a = src.q2.get()
                if dst.q.qsize() < dst.numberOfClients:
                    dst.q.put(a)
                    break
                else:
                    dst.q2.put(a)
                event.clear()
                #print("PREPISUJEM {} iz {} u {}".format(a, src, dst))
                #dst.q2.put(a)
                #send.wait()
    
    """
    1. izracunati koliko krugova ce obici poruke u grafu
    2. pomnoziti broj krugova sa brojem klijenata svakog cvora
    3. ostaviti taj broj u q, a ostalo prebaciti u q2
    4. poruke koje se nalaze u q2 kruze kroz graf
    
    
    def read_from_broker_queue(self):
        global endMessage
        while True:
            #event.wait()
            while self.q.qsize() < self.numberOfClients and endMessage == False:
                print("GARIIIIIII MOOOOJ")
                data = self.q2.get()
                self.q.put(data)
            #event.clear()
    """
    
        
#graph       
class Graph:
    nodes = list()
    edges = list()
    cnt = 0

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
            #s.start_queue_exchange()
            print("Sacekao sam konekcije")
        elif flag == 2:
            #for c in s.clientList:
            s.threaded_client()
            print("GARISONER {}".format(s))
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
                        #broker.start_queue_exchange()
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
    """
    max_char = 12
    min_char = 8
    cnt = 0
    ukupnoPoruka = 0
    for i in range(nodes):
        cnt = 0
        while cnt < 10:
            ukupnoPoruka += 1
            allchar = string.ascii_letters + string.digits
            data = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
            objs[i].q.put(data)
            cnt = cnt + 1
            time.sleep(.1)
        #objs[0].q.put("GArisa")
    print("IMAM OVOLIKO CNT {}".format(ukupnoPoruka))
    """
                
    
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
P1 = Publisher("Publisher")
t1 = threading.Thread(target=P1.generate_string, args=[graph.nodes[0]])
tic = time.perf_counter()
t1.start()
print("Flag set")
print("DUZINA GRAFA {}".format(len(graph.nodes)))
flag = 2 
"""
for c in graph.nodes[0].clientList:
    print("Node 0 {}".format(c))
print("Broker 2")
for c in graph.nodes[1].clientList:
    print("Node 1 {}".format(c))
"""

#time.sleep(10)

while True:
    graph.BFS(graph.nodes[0])
    if totalMessagesSentCount == 100:
        print("USAO SAM NA KRAJ")
        toc = time.perf_counter()
        break

print("CLOSING CONNECTION")
CPU_Pct = str(round(float(os.popen('''grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage }' ''').readline()),2))
#print results
print("CPU Usage = " + CPU_Pct)
print("Elapsed time: {}".format(toc - tic))
print()
print(f"Max Frequency: {cpufreq.max:.2f}Mhz")
print(f"Min Frequency: {cpufreq.min:.2f}Mhz")
print(f"Current Frequency: {cpufreq.current:.2f}Mhz")
print()
print("CPU Usage Per Core:")
for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
    print(f"Core {i}: {percentage}%")
print(f"Total CPU Usage: {psutil.cpu_percent()}%")

svmem = psutil.virtual_memory()
print(f"Total: {get_size(svmem.total)}")
print(f"Available: {get_size(svmem.available)}")
print(f"Used: {get_size(svmem.used)}")
print(f"Percentage: {svmem.percent}%")
print("="*20, "SWAP", "="*20)
# get the swap memory details (if exists)
swap = psutil.swap_memory()
print(f"Total: {get_size(swap.total)}")
print(f"Free: {get_size(swap.free)}")
print(f"Used: {get_size(swap.used)}")
print(f"Percentage: {swap.percent}%")

flag = 3
graph.BFS(graph.nodes[0])
#interate through the graph to close connections
print("Closing connections")
#graph.BFS(graph.nodes[0]) 
ServerSocket.close()
print("\n\nExit program\n")
sys.exit()
