from enum import Enum
from dataclasses import dataclass

from client import Client
from messages import Message, parse_message_data_string

# =============================================================================
# Here lies all commands possible with our echo client:
#
# Commands are simple structs holding a command type and any related operands.
# Command logic is defined in single functions which operate on Client objects.
# =============================================================================

# ------------------
# Command Procedures
# ------------------

# -----------------------------
#     HELP/STATUS/SET/QUIT
# miscellaneous client commands
# -----------------------------

# HELP
# Prints instructions on how to use the client
def cmd_help(operands: list[str]):
    cmds = operands
    if len(cmds) == 0:
        print(" [Commands]: ")
        print("  [Client]:")
        print("   * help * status * set * quit")
        print("  [Messages]:")
        print("   * write * view * edit * clear * send * simple")
        print("  [Inbox]:")
        print("   * read * delete * empty")
        print("  [Connection]:")
        print("   * host * port * connect * disconnect\n")
        print("  Run this command with commands or command groups you want help with (or all for all commands)")
        print("  ex: 'help status' / 'help write status delete' / 'help messages' / 'help all'\n")

        print(" [Client Flags]: ")
        print("  * logging      enable logging of client operations")
        print("  * force        disable message overwrite protection")
        print("  * rawread      disable message modifier formatting")
        print("  * instantsend  instantly send a message on write")
        print("  * instantread  instantly read a message on echo recieve")
        print("  * burnonsend   clear your message after sending")
        print("  * burnonread   delete your recieved echos once read\n")

        print(" [Writing Messages]:")
        print("  Message modifiers begin with ';'.")
        print("  The first word without the modifier prefix is considered the start of your message.")
        print("  (if your message must start with a ';' or whitespace, use ;text to begin your message)")
        print("  modifiers: ;noecho | ;caps | ;reverse | ;text yourmessagehere\n")

        print(" [Message Modifiers]:")
        print("  Our message format supports the following modifiers:")
        print("  * ;noecho   disable display of the message echo")
        print("  * ;caps     capitalize all letters")
        print("  * ;reverse  reverse the message")
        print("  * ;text     explicitly begin your message's text")
    else:
        if "all" in cmds: cmds = ["client", "messages", "inbox", "connection"]
        if "client" in cmds:
            cmds += ["help", "status", "set", "quit"]
            cmds.remove("client")
        if "messages" in cmds:
            cmds += ["write", "view", "edit", "clear", "send", "simple"]
            cmds.remove("messages")
        if "inbox" in cmds:
            cmds += ["read", "delete", "empty"]
            cmds.remove("inbox")
        if "connection" in cmds:
            cmds += ["host", "port", "connect", "disconnect"]
            cmds.remove("connection")
        cmds = list(dict.fromkeys(cmds)) # remove duplicates
    for cmd in cmds:
        match cmd:
            case "help":
                print(" [help]")
                print("  lends a helping hand")
                print("  ex: 'help' / 'help all'")
            case "status":
                print(" [status]")
                print("  displays the current state of the client")
                print("  ex: 'status'")
            case "write":
                print(" [write]")
                print("  write a message to the client's write buffer")
                print("  ex: 'write yourmsghere' / 'write ;mod1 ;mod2 ... yourmsghere'")
            case "set":
                print(" [set]")
                print("  sets a client flag on or off")
                print("  ex: 'set instantsend on' / 'set instantread off'")
            case "quit":
                print(" [quit]")
                print("  shuts down connection and quits the client")
                print("  ex: 'quit'")
            case _:
                print(f" ! can't help you with '{cmd}'")

# STATUS
# Displays the state of the client's components
def cmd_status(client: Client):
    client_state = client.get_state()

    print(f" Connection: {client_state["connection"]}")
    print(f" Host: {client_state["connectionhost"]}")
    print(f" Port: {client_state["connectionport"]}\n")

    print(f" Write Buffer: {client_state["messagebuffer"]}")
    print(f" Inbox: {client_state["recievebuffer"]}\n")

    for flag in client_state["flags"]:
        print(f"  {flag}: {client_state["flags"][flag]}")

# SET
# Toggle parts of the client on/off
def cmd_set(client: Client, operands: list[str]):
    if len(operands) != 2:
        print(" ! bad set command, must be 3 words (set flag on/off)")
        return

    flag = operands[0]
    onoff = operands[1]
    if flag in client.flags:
        if onoff in ["on", "off"]:
            client.flags[flag] = onoff == "on"
            print(f" {flag}: {client.flags[flag]}")
        else: print(f" ! flags can only be set on or of, not '{operands[1]}'")
    else: print(f" ! unknown client setting '{flag}'")

# QUIT
# Closes the connection, sets the client's kill signal
def cmd_quit(client: Client):
    client.shutdown()

# ---------------------------------
# WRITE/VIEW/EDIT/CLEAR/SEND/SIMPLE
#         message commands
# ---------------------------------

# WRITE
# Creates a Message from string & writes it to the client's write buffer
def cmd_write(client: Client, operands: list[str]):
    if len(operands) > 0: msg_definition_str = operands[0]
    else: msg_definition_str = ""   # allow for blank messages
    mess = Message(parse_message_data_string(msg_definition_str)) # @? should parsing the message data be done HERE or in MESSAGES?
    client.message_write(mess)

# VIEW
# View the message in buffer
def cmd_view(client: Client):
    client.message_view()

# EDIT
# Edit the message in buffer
def cmd_edit(client: Client, operands: list[str]):
    if len(operands) > 0: msg_definition_str = operands[0]
    else: msg_definition_str = ""   # allow for empty edits
    client.message_edit(parse_message_data_string(msg_definition_str))

# CLEAR
# Clear message from client write buffer
def cmd_clear(client: Client):
    client.message_clear()

# SEND
# Send message in buffer over connection
def cmd_send(client: Client):
    client.message_send()

# SIMPLE
# Basic send and echo mode, loops writing and sending a new message each input
def cmd_simple(client: Client):
    print(" entering simple echo mode")
    print(" type 'complex' before your message text/modifiers to quit\n")

    # Change needed flags for simple echo mode
    flagstates = {"force":client.flags["force"],
                  "instantsend":client.flags["instantsend"],
                  "instantread":client.flags["instantread"],
                  "burnonsend":client.flags["burnonsend"]}
                  #"burnonread":client.flags["burnonread"]}

    client.flags["force"] = True
    client.flags["instantsend"] = True
    client.flags["instantread"] = True
    client.flags["burnonsend"] = True
    #client.flags["burnonread"] = True

    # Write input loop
    inpt = input(": ")
    while inpt != "complex":
        command_run(client, command_get("write " + inpt))
        inpt = input(": ")

    print( "exiting simple echo mode")

    # Restore flag states
    for flag in flagstates:
        client.flags[flag] = flagstates[flag]

# -----------------
# READ/DELETE/EMPTY
#  inbox commands
# -----------------

# READ
# Read one, all, or most recent message in inbox
def cmd_read(client: Client, operands: list[str]):
    if len(operands) > 1:
        print(" ! bad read command, must be 1 or 2 words (read / read all / read n)")
        return
    if len(operands) == 0: client.inbox_read_top()                    # No operands, read top
    elif operands[0] == "all": client.inbox_read_all()                # "All", list entire inbox
    elif operands[0].isdigit(): client.inbox_read(int(operands[0])-1) # Int, read msg at index
    else: print(f" ! can't read '{operands[0]}', only (read / read all / read n) accepted")

# DELETE
# Delete a specific number in inbox
def cmd_delete(client: Client, operands: list[str]):
    if len(operands) != 1:
        print(" ! bad delete command, must be 2 words (delete n)")
        return
    if operands[0].isdigit(): client.inbox_delete(int(operands[0])-1)
    else: print(f" ! can't delete '{operands[0]}', must be inbox message number")

# EMPTY
# Delete entire inbox
def cmd_empty(client: Client):
    client.inbox_empty()

# ----------------------------
# HOST/PORT/CONNECT/DISCONNECT
#     connection commands
# ----------------------------

# Set the client's connection socket host
def cmd_host(client: Client, operands: list[str]):
    if len(operands) != 1:
        print(" ! bad host command, must be 2 words (host 127.0.0.1)")
        return
    client.connection_set_ip(operands[0])

# Set the client's connection socket port 
def cmd_port(client: Client, operands: list[str]):
    if len(operands) != 1:
        print(" ! bad port command, must be 2 words (port 31800)")
        return
    if operands[0].isdigit(): client.connection_set_port(int(operands[0]))
    else: print(f" ! can't set port to '{operands[0]}', must be int")

# Activate the client's connection socket
def cmd_connect(client: Client):
    client.connection_establish()

# Disconnect the client's connection socket
def cmd_disconnect(client: Client):
    client.connection_close()

# =============================================================================

# ----------------------
# Command Types and Data
# ----------------------

# Types of commands in the client + associated procedures
class CommandCode(Enum):
    Null    = None
    # Client misc
    Help    = cmd_help #0            # Help text
    Status  = cmd_status #1          # Client state
    Set     = cmd_set #3             # Set a client flag
    Quit    = cmd_quit #4
    # Message making
    Write   = cmd_write  #2           # Write message
    View    = cmd_view #5            # View message written in buffer
    Edit    = cmd_edit #6            # Edit message written in buffer
    Clear   = cmd_clear     # clear message in buffer
    Send    = cmd_send      # send message in buffer
    Simple  = cmd_simple              # keep write mode
    # Inbox
    Read    = cmd_read # read top message
    Delete  = cmd_delete # delete at inbox index 
    Empty   = cmd_empty # delete all
    # Connection
    Host    = cmd_host       # set socket host
    Port    = cmd_port    # set socket port
    Connect     = cmd_connect  # connect to socket
    Disconnect  = cmd_disconnect # disconnect from socket

# Command data container 
@dataclass
class Command():
    opcode: CommandCode     # Command type and related procedure
    operands: list[str]     # List of string word operands
    signature: int          # Arguments needed by command procedure

# =============================================================================

# ----------------------------
# Getting and Running Commands
# ----------------------------

# COMMAND_GET
# Returns a Command dataclass interpreted from the given string
def command_get(inpt: str) -> Command:
    # Process words of command
    cmdwords = inpt.lower().split()

    # If operands given, add them
    if len(cmdwords) > 1: operands = cmdwords[1:]
    else: operands = []

    # Set opcode and signature
    opcode = CommandCode.Null   # Default null command
    signature = 0b00            # Empty signature
    if len(cmdwords) > 0:
        match cmdwords[0]:
            case "help":
                opcode = CommandCode.Help
                signature = 0b01
            case "status":
                opcode = CommandCode.Status
                signature = 0b10
            case "set":
                opcode = CommandCode.Set
                signature = 0b11
            case "quit":
                opcode = CommandCode.Quit
                signature = 0b10
            case "write":
                opcode = CommandCode.Write
                signature = 0b11
                # Special operand case: use single raw input string to preserve text spacing
                if len(operands) > 0: operands = [inpt[6:]]
            case "view":
                opcode = CommandCode.View
                signature = 0b10
            case "edit":
                opcode = CommandCode.Edit
                signature = 0b11
                # Special operand case: use single raw input string to preserve text spacing
                if len(operands) > 0: operands = [inpt[5:]]
            case "clear":
                opcode = CommandCode.Clear
                signature = 0b10
            case "send":
                opcode = CommandCode.Send
                signature = 0b10
            case "simple":
                opcode = CommandCode.Simple
                signature = 0b10
            case "read":
                opcode = CommandCode.Read
                signature = 0b11
            case "delete":
                opcode = CommandCode.Delete
                signature = 0b11
            case "empty":
                opcode = CommandCode.Empty
                signature = 0b10
            case "host":
                opcode = CommandCode.Host
                signature = 0b11
            case "port":
                opcode = CommandCode.Port
                signature = 0b11
            case "connect":
                opcode = CommandCode.Connect
                signature = 0b10
            case "disconnect":
                opcode = CommandCode.Disconnect
                signature = 0b10
            case _:
                print(f" ! unknown command '{inpt}'")

    return Command(opcode, operands, signature)

# COMMAND_RUN
# Executes the given command's procedure on a Client object
def command_run(client: Client, cmd: Command) -> bool:
    success = True
    if cmd.opcode != CommandCode.Null:
        match cmd.signature:
            case 0b01: cmd.opcode(cmd.operands)
            case 0b10: cmd.opcode(client)
            case 0b11: cmd.opcode(client, cmd.operands)
            case _:
                success = False
                print(" ! bad command signature, how did that happen?")
    else:
        print(" hint: use the 'help' command")
        success = False
    print() # newline between commands
    return success


