from messages import Message, encode_message, decode_message, parse_message_command
from sock import socketConnection

# Client

# COMPOSED OF:
#
# Socket connection
# Single message to send
# Queue of messages recieved

# FUNCTIONALITY:
#
# Establish a connection
# Destroy a connection
#
# Create and specify details of a message
# 
# Send message over connection
#   Send ONE message at a time
# Recieve message over connection
#   Recieve MULTIPLE messages at a time, need SEPERATE THREAD
#

class Client():
    def __init__(self):
        self.message = None     # Message written from client
        self.recieved = []      # Messages recieved to client
        self.connection = socketConnection()    # Socket manager
        #self.listener

        self.flags = {"logging"     : False,
                      "instantsend" : True,
                      "instantread" : True,
                      "force"       : False}


        ## Various flags for client functionality
        self.fl_logging = False     # Flag for logging
        self.fl_instant = True      # Flag for instant send mode
        self.fl_listen = False      # Flag for recieving in background (instead of halting program for response)
        self.fl_force = True #False       # Flag for forcing some commands

        ## burn on read, burn on send

    def message_write(self, msg: Message):#, details: dict = {}):  # Details dict defines initial components of message
        if self.message != None:
            if not self.fl_force:
                print("WARN: Message still exists in buffer, set the 'force' flag to override")
                return
            else: self.message_clear()
        if self.fl_logging: print("CLOG: Writing a message to buffer")
        self.message = msg              #Message(parse_message_command(input(" Write: ")))
        if self.fl_instant:
            self.message_send()
        #    self.message_wait_for_recieve() threaded listerner DO!
            if self.fl_logging: print("CLOG: Waiting for recieve...")
            self.recieved.append(decode_message(self.connection.recv_msg()))
            self.display_message(self.recieved.pop())


    def message_clear(self):
        if self.fl_logging: print("CLOG: Clearing message in buffer")
        self.message = None

    # message_display() 

    def message_send(self):
        if self.fl_logging: print("CLOG: Sending message in buffer through socket")
        self.connection.send_msg(encode_message(self.message))

    def display_message(self, msg: Message):
        print(f'text: "{msg.text}"')
        print(f"echo: {msg.echo}")

    def connection_set_ip(self, ip: str):
        if self.fl_logging: print(f"CLOG: Setting connection host to {ip}")
        # @todo do some checking here for bad ips (or should that be done in command_interpret?)
        self.connection.host = ip

    def connection_set_port(self, port: int):
        if self.fl_logging: print(f"CLOG: Setting connection port to {port}")
        self.connection.port = port

    def connection_establish(self):
        if self.fl_logging: print("Establishing connection")
        self.connection.open()
        print(self.connection.recv_msg().decode()) # Welcome from server

    def connection_close(self):
        if self.fl_logging: print("Closing connection")
        self.connection.close()








## COMPOSITIONAL MODE!
## Client can write and edit a message, keep it in the buffer before sending!
## DIRECT MODE
## Client writes a message and it sends immediatly

## We want the message to stay stored as long as it hasn't been echo'd back yet
## The user should be able to resend that message too, or perhaps edit it? They at least need to be able to view it!

## message not echo'd pack, resend?
## message not echo'd pack, are you sure you want to wipe and write another?


