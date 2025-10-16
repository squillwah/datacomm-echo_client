from messages import Message, encode_message, decode_message, stringify_message_fancy, stringify_message_raw
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
        self._message = None     # Message written from client
        self._recieved = []      # Messages recieved by client
        self._connection = socketConnection()    # Socket manager
        #self.listener

        self.flags = {"logging"     : False,    # Client logs its operations to screen
                      "force"       : False,    # Let messages in buffer be written over
                      "rawread"     : False,    # Messages are read unformatted by modifiers
                      "instantsend" : True,     # Instantly send a message once written
                      "instantread" : True,     # Instantly read a message once recieved
                      "burnonsend"  : True,     # Clear the message buffer on send
                      "burnonread"  : True}     # Delete the recieved message once read

        self.killme = False     # Signal client manager to stop processing this client


    #def run()
    #    self._running = True
    #def stop()
    #    self._running = False


    def message_write(self, msg: Message):#, details: dict = {}):  # Details dict defines initial components of message
        if self._message != None:
            print(" ! message in buffer")
            if self.flags["force"]:
                print(" ! force flag set, writing anyways")
                self.message_clear()
            else:
                print(" ! cancelling write, set the 'force' flag to override")
                return

        if self.flags["logging"]: print(" . writing message to buffer")
        self._message = msg
        if self.flags["instantsend"]: self.message_send()
        if self.flags["instantread"]: self.display_message(self._recieved.pop())

    def message_clear(self):
        if self.flags["logging"]: print(" . clearing message in buffer")
        self._message = None

    def message_send(self):
        if self.flags["logging"]: print(" . sending message in buffer through socket")
        self._connection.send_msg(encode_message(self._message))
        if self.flags["burnonsend"]: self.message_clear()

        # @todo move this to threaded reciever/listener
        if self.flags["logging"]: print(" . waiting for recieve...")
        self._recieved.append(decode_message(self._connection.recv_msg()))

    def display_message(self, msg: Message):
        #print(f'text: "{msg.text}"')
        #print(f"echo: {msg.echo}\n")

        print(f" {stringify_message_fancy(msg)}")
        print(f" {stringify_message_raw(msg)}")

    #def message_view()
    #def message_edit()
    #def inbox_view()
    #def inbox_empty()

    def connection_set_ip(self, ip: str):
        if self.flags["logging"]: print(f"CLOG: Setting connection host to {ip}")
        # @todo do some checking here for bad ips (or should that be done in command_interpret?)
        self._connection.host = ip

    def connection_set_port(self, port: int):
        if self.flags["logging"]: print(f"CLOG: Setting connection port to {port}")
        self._connection.port = port

    def connection_establish(self):
        if self.flags["logging"]: print("Establishing connection")
        self._connection.open()
        print(self._connection.recv_msg().decode()) # Welcome from server

    def connection_close(self):
        if self.flags["logging"]: print("Closing connection")
        self._connection.close()

    def get_state(self) -> dict:
        state = {"connection":((self._connection.sock is not None)*"Active" + (self._connection.sock is None)*"Disconnected"),
                 "messagebuffer":((self._message is not None)*"Occupied" + (self._message is None)*"Empty"),
                 "recievebuffer":(str(len(self._recieved)) + " messages"),
                 "flags":{}}
        for flag in self.flags:
            state["flags"][flag] = self.flags[flag]*"on" + (not self.flags[flag])*"off"
        return state




            #    self.message_wait_for_recieve() threaded listerner DO!
    # message_display() 







## COMPOSITIONAL MODE!
## Client can write and edit a message, keep it in the buffer before sending!
## DIRECT MODE
## Client writes a message and it sends immediatly

## We want the message to stay stored as long as it hasn't been echo'd back yet
## The user should be able to resend that message too, or perhaps edit it? They at least need to be able to view it!

## message not echo'd pack, resend?
## message not echo'd pack, are you sure you want to wipe and write another?


