from threading import Thread

from messages import Message, encode_message, decode_message, stringify_message_fancy, stringify_message_raw
from sock import socketConnection

# =============================================================================
# Echo Client
#
# The echo client consists of:
#  * a user written message, which can be stored, edited, and sent to the server
#  * an inbox of messages recieved from the server, which can be viewed and emptied 
#  * a socket connection to the server, wherein the ip and port can be specified
#  * a threaded reciever, which silently processes bytes recieved on the connection
#  * various settings which tweak the functionality of the client's operations
#
# The user interacts with the client through a command system defined in commands.py
# =============================================================================

class Client():
    # --------------
    # Initialization
    # --------------

    def __init__(self):
        self._message = None                    # Message written from client
        self._inbox = []                        # Messages recieved by client
        self._connection = socketConnection()   # Socket manager

        self._ls_thread = Thread(target=self._listener_process) # Listener thread
        #self._ls_buffer = b""                                   
        self._ls_running = False            # Controls the listener recieve loop
        self._ls_signal_recieved = False    # Signals True when a recieve occured

        self.flags = {"logging"     : False,    # Client logs its operations to screen
                      "force"       : False,    # Let messages in buffer be written over
                      "rawread"     : False,    # Messages are read unformatted by modifiers
                      "instantsend" : True,     # Instantly send a message once written
                      "instantread" : True,     # Instantly read a message once recieved
                      "burnonsend"  : True,     # Clear the message buffer on send
                      "burnonread"  : True}     # Delete the recieved message once read

        self.killme = False     # Signal client manager to stop processing this client

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
            if self.flags["logging"]: print(" . message recieved")

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

    # -------------------------
    # Creating/Sending Messages
    # -------------------------

    # Writes a message object to empty message buffer
    #  Optionally overwrite occupied buffer with 'force' 
    #  Optionally send message instantly with 'instantsend' 
    def message_write(self, msg: Message):
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

    # Edits parts of the message in the buffer via dict w/ message component keys
    def message_edit(self, changes: dict):
        if self._message == None:
            print(" ! no message in buffer to edit")
            return

        if self.flags["logging"]: print(" . updating message")
        modify_message(self._message, changes)

    # Displays the written message in the buffer
    def message_view(self):
        if self._message == None:
            print(" ! no message in buffer to view")
            return

        print(f" {stringify_message_raw(self._message)}")

    # Clears the message in the buffer
    def message_clear(self):
        if self._message == None:
            print(" ! no message in buffer to clear")
            return

        if self.flags["logging"]: print(" . clearing message in buffer")
        self._message = None

    # Sends the message in the buffer through the connection socket
    #  Optionally wait for and read the recieved echo with 'instantread'
    #  Optionally clear the message buffer on send with 'burnonsend'
    def message_send(self):
        if self._connection.host == None:
            print(" ! connection is closed, aborting send")
            return

        # Clear the listener's recieved signal
        self._ls_signal_recieved = False

        # Encode+send message
        if self.flags["logging"]: print(" . encoding message in write buffer")
        msgbytes = encode_message(self._message)
        if self.flags["logging"]: print(" . sending encoded message through socket")
        self._connection.send_msg(msgbytes)

        # Delete message if set to burnonsend
        if self.flags["burnonsend"]: self.message_clear()

        # If in instantread mode, wait for the recieve signal then display
        if self.flags["instantread"]:
            if not self._ls_signal_recieved:
                if self.flags["logging"]: print(" . waiting for recieve")
                while not self._ls_signal_recieved: pass
            self.inbox_read_top()

    #def message_recieve() #? should we even bother with the thread, or should we silently halt until its recieved?

    def display_message(self, msg: Message):
        print(f" {stringify_message_fancy(msg)}")
        print(f" {stringify_message_raw(msg)}")

    # =========================================================================

    # ----------------------
    # Reading/Emptying Inbox
    # ----------------------

    #read to view most recent message
    #read all to view all message in inbox

    # Displays the most recent message added to inbox
    #  Optionally delete the message with 'burnonread'
    #  Optionally display raw message data with 'rawread'
    def inbox_read_top(self):
        if len(self._inbox) == 0:
            print(" ! inbox empty")
            return

        reader = stringify_message_fancy
        if self.flags["rawread"]: reader = stringify_message_raw

        messindex = len(self._inbox)-1
        print(f"\n  {reader(self._inbox[messindex])}\n")

        if self.flags["burnonread"]: self.inbox_delete(self, messindex))

    # Displays all messages in inbox
    #  Optionally empty inbox with 'burnonread'
    #  Optionally display messages raw with 'rawread'
    def inbox_read_all(self):
        if len(self._inbox) == 0:
            print(" ! inbox empty")
            return

        reader = stringify_message_fancy
        if self.flags["rawread"]: reader = stringify_message_raw

        print()
        for messindex in range(len(self._inbox), 0):
            print(f"  {messindex}. {reader(self._inbox(messindex)}")
        print()

        if self.flags["burnonread"]: self.inbox_empty()

    # Delete message at index in inbox
    def inbox_delete(self, index: int):
        if index < 0 or >= len(self._inbox):
            print(f" ! inbox message {index+1} doesn't exist")
            return

        if self.flags["logging"]: print(f" . deleting message {index+1}")
        del self._inbox[index]

    # Delete all messages in inbox
    def inbox_empty(self):
        if len(self._index) == 0:
            print(f" ! inbox already empty")
            return

        if self.flags["logging"]: print(f" . emptying message {index+1}")
        for i in range(0, len(self._inbox)): self.inbox_delete(i)
        # alternatively: self._inbox = []


    # =========================================================================

    # ----------------------------------
    # Setting/Opening/Closing Connection
    # ----------------------------------

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

    # =========================================================================

    # ---------------------
    # Meta Client Functions
    # ---------------------

    # Returns a dict describing the state of each client component
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

    # Gracefully shutdown the client
    #def shutdown(self):
    #    self.connection_close()
    #    # stop the listener
    #    self.killme = True






## COMPOSITIONAL MODE!
## Client can write and edit a message, keep it in the buffer before sending!
## DIRECT MODE
## Client writes a message and it sends immediatly

## We want the message to stay stored as long as it hasn't been echo'd back yet
## The user should be able to resend that message too, or perhaps edit it? They at least need to be able to view it!

## message not echo'd pack, resend?
## message not echo'd pack, are you sure you want to wipe and write another?


