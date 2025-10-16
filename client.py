from threading import Thread

from messages import Message, encode_message, decode_message, stringify_message_fancy, stringify_message_raw
from sock import socketConnection
#from listener import Listener

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
        self._inbox = []         # Messages recieved by client
        self._connection = socketConnection()       # Socket manager

        self._ls_thread = Thread(target=self._listener_process)
        self._ls_buffer = b""
        self._ls_running = False
        self._ls_signal_recieved = False

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

    # =========================================================================

    # ------------------ 
    # Threaded Recieving
    # ------------------

    # The listener process
    # Waits for recieves from socket, appends decoded bytes to client inbox
    def _listener_process(self):
        while(self._ls_running):
            #self._ls_buffer += self._connection.recv_msg()
            data = self._connection.recv_msg() # THIS COULD CAUSE ISSUE WITH INCOMPLETE MESSAGES MAYBE MAYBE MAYBE!

            ## Search buffer for a valid message wrapped in the message key
            #buffer_string = str(ls_buffer)
            #mess_start = buffer_string.find(Message.FORMAT_KEYS["all"][0])
            #mess_end = buffer_string.find(Message.FORMAT_KEYS["all"][1])

            #if mess_start != -1 and mess_end != -1:
            #    self._inbox

            self._inbox.append(decode_message(data)) # @todo implement multi message decode and bad message conditions in decode_message
            self._ls_signal_recieved = True

    # Start the listener thread
    def _listener_start(self):
        self._ls_running = True
        self._ls_thread.start()

    # Stop the listener thread
    def _listener_stop(self):
        self._ls_running = False
        self._connection.send_msg(b"Bye!")  # Default rcv causes hanging (no timeout), must send final msg for it to grab
        self._ls_thread.join()

    # =========================================================================

    # ---------------------------------
    # Creating/Editing/Sending Messages
    # ---------------------------------

    def message_write(self, msg: Message):#, details: dict = {}):  # Details dict defines initial components of message
        if self._message != None:
            print(" ! message in buffer")
            if self.flags["force"]:
                print(" ! force flag set, writing anyways")
                self.message_clear()
            else:
                print(" ! cancelling write, clear write buffer or set the 'force' flag to override")
                return

        if self.flags["logging"]: print(" . writing message to buffer")
        self._message = msg
        if self.flags["instantsend"]: self.message_send()
        #if self.flags["instantread"]: self.display_message(self._recieved.pop()) # should this only be in listener?

#        # instant read == wait to recieve echo before moving on
#        recievedsize = len(self._recieved)
#        self.message_send()
#        while(len(self._recieved) == recievedsize) # wait before recieve

        #NO!
        #NO THREAD!
        # start a timeout
        # currentrecieved = len(self._recieved)
        # sendtime
        # self.message_send()
        # while(len(self._recieved) ==

        # clear listener recieve flag
        # wait while flag is not set
        # then print the message

        # should while loop here to wait for recieve listener with instant read?

    def message_clear(self):
        if self.flags["logging"]: print(" . clearing message in write buffer")
        self._message = None

    def message_send(self):
        # Clear the recieved signal
        if self.flags["instantread"]: self._ls_signal_recieved = False

        # Encode+send message, clear from buffer is burnonsend
        if self.flags["logging"]: print(" . encoding message in write buffer")
        msgbytes = encode_message(self._message)
        if self.flags["logging"]: print(" . sending encoded message through socket")
        self._connection.send_msg(msgbytes)
        if self.flags["burnonsend"]: self.message_clear()

        # If in instantread mode, wait for the recieve signal then display
        if self.flags["instantread"]:
            if self.flags["logging"]: print(" . waiting for recieve (instantread set)")
            while not self._ls_signal_recieved: pass
            self.display_message(self._inbox.pop())




        #if self.flags["logging"]: print(" . waiting for recieve...")
        #self._recieved.append(decode_message(self._connection.recv_msg()))

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
        if self.flags["logging"]: print(" . establishing connection")
        self._connection.open()
        print(f" The server says: {self._connection.recv_msg().decode()}") # Welcome from server
        if self.flags["logging"]: print(" . starting listener thread")
        self._listener_start()

    def connection_close(self):
        if self.flags["logging"]: print(" . stopping listener thread")
        self._listener_stop()
        while self._ls_running: pass
        if self.flags["logging"]: print(" . closing connection")
        self._connection.close()

    def get_state(self) -> dict:
        state = {"connection":((self._connection.sock is not None)*"Active" + (self._connection.sock is None)*"Disconnected"),
                 "connectionhost":self._connection.host,
                 "connectionport":self._connection.port,
                 "messagebuffer":((self._message is not None)*"Occupied" + (self._message is None)*"Empty"),
                 "recievebuffer":(str(len(self._inbox)) + " messages"),
                 "flags":{}}
        for flag in self.flags:
            state["flags"][flag] = self.flags[flag]*"on" + (not self.flags[flag])*"off"
        return state

    def shutdown(self):
        self.connection_close()
        # stop the listener
        self.killme = True




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


