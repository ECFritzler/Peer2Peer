# CPSC 3780 - Data Comm & Networking
# Peer-to-peer Chat Application Project
# Claire Fritzler and Corwin Smith

# The program will discover any other chat applications running in the labs
# IP Ranges:  C-LAB: 142.66.140.21-45. D-LAB: 142.66.140.46-69, and 142.66.140.186
# Port Ranges: 55000 - 55008
# A one line message will be sent to all active users
# Peer Discovery: To discover peer applications, the receiver

from queue import Queue, Empty
from threading import Thread, Timer
from time import sleep
import threading
import sys, socket, errno
import json

MYPORT = int(sys.argv[1])

PORTRANGE = [55000, 55001, 55002, 55003, 55004, 55005, 55006, 55007, 55008]
IPADDRESSRANGE=['142.66.140.186']
BUFLEN = 1000

for ip in range(21,70):
    IPADDRESSRANGE.append('142.66.140.'+str(ip))
# Receiver class
# If the reciver receives a "Hello" message, then it must add that
# user (username) to the list and start the timer.
class Receiver(Thread):
    def __init__(self, queue, username):
        Thread.__init__(self)
        self.queue = queue
        self.username = username
        self.partners = []

    def remove_partner(self):
        print(self.partners)

    def run(self):
        try:
            s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print ("Cannot open socket")
            sys.exit(1)

        try:
            s.bind(('',MYPORT))
        except:
            print ("Cannot bind my socket to port")
            sys.exit(1)

        while True:
            try:
                data, addr = s.recvfrom(BUFLEN)
                # print(data, addr)
                #print(addr[0], " + ", addr[1])
                #print(data)
            except OSError as err:
                print ("Cannot receive from socket: {}".format(err.strerror))

            if(data[:5] == b'HELLO'):
                # If the timer reaches 0, remove the partner from the list
                # If a hello message is received and the partner is already in
                # the list, update the timer
                for elem in self.partners:
                    if elem[0] == addr and elem[1] == data[6:]:
                        self.partners.remove(elem)
                for IP in IPADDRESSRANGE:
                    for PORT in PORTRANGE:
                        if((IP, PORT) == addr):
                            self.partners.append([IP, PORT-1, data[6:]])
                            
               # timer = Timer(15.0, lambda: remove_partner(self))
               # timer.start() s.bind(
                #try:
                  #  for i in range(0, len(self.partners)-1):
                   #     if(self.partners[i][0] == username and self.partners[i][1] == addr):
                    #        self.partners.remove(i)

                     #       self.partners.append([username, addr, timer])
                      #  else:
                       #     self.partners.append([username, addr, timer])
                #except:
                 #   print ("No partners")

                # Print all incoming messages that are not from ourselves
            else:
                if(addr[1] != MYPORT+1):
                    print(data)



# Hello Thread.
# Sends a "HELLO" message every 5 seconds so that other users on the
# network can add to their active user lists
class Hello(Thread):
    def __init__(self, username):
        Thread.__init__(self)
        self.username = username

    def hello(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            print ("Cannot open socket")
            sys.exit(1)

        try:
            s.bind(('', MYPORT+1))
        except:
            print ("Cannot bind HELLO to port")
            sys.exit(1)

        try:
            string = str.encode('HELLO ' + self.username)
           
            for IP in IPADDRESSRANGE:
                for PORT in PORTRANGE:
                    s.sendto(string, (IP, PORT))
        except OSError as err:
            print ('Cannot send: {}'.format(err.strerror))
            sys.exit(1)

    def run(self):
        while True:
            sleep(5.0)
            s.close()
            self.hello()

def check_username(username):
    check = True
    for letter in username:
        if(letter.isalnum() or letter=='_' or letter=='-' or letter=='.'):
            check = True
        else:
            check = False
            break
    return check

def main():
    print("Please enter a username")
    username = input('')
    check = check_username(username)
    while(check==False):
        print("Reenter a valid unsername")
        username = input('')
        check = check_username(username)
   
    queue = Queue()
    r = Receiver(queue, username)
    r.daemon = True
    r.start()
    h = Hello(username)
    h.daemon = True
    h.start()

    print ('s <msg> - sends message \nq-quits\n')
    cmd = input('')
    while cmd[0] != 'q':
        if cmd[0] is 's':
            message = username+': '
            for char in range(2, len(cmd)):
                message += cmd[char]

            chat_message = message
            chat_message=json.dumps(chat_message).encode('utf-8')

            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except:
                print("Cannot open socket")
                sys.exit(1)
            try:
                s.bind(('', MYPORT+1))
            except:
                print("Cannot bind socket to port")
               
           # try:
            #    for IP in IPADDRESSRANGE:
             #       for PORT in PORTRANGE:
              #          s.sendto(chat_message, (IP, PORT))
            try:
                for partner in r.partners:
                    print(partner)
                    #send_message = str.encode(message)
                    s.sendto(chat_message, (partner[0], partner[1]))
            except OSError as err:
                print('Cannot send: {}'.format(err.strerror))
                sys.exit(1)
        cmd = input('')

print('So long partner')


main()
