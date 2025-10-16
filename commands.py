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
# Command procedures
# ------------------

# HELP
# Prints instructions on how to use the client
def cmd_help(operands: list[str]):
    cmds = operands
    if len(cmds) == 0:
        print(" [Commands]: ")
        print("  * help")
        print("  * status")
        print("  * write")
        print("  * set")
        print("  * quit\n")
        print("  Run this command with commands you want help with (or all for all commands)")
        print("  ex: 'help status' / 'help write status' / 'help all'\n")

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
        print("  (if your message must start with a ';', use ;text to begin your message)")
        print("  modifiers: ;noecho | ;caps | ;reverse | ;text yourmessagehere\n")

        print(" [Message Modifiers]:")
        print("  Our message format supports the following modifiers:")
        print("  * ;noecho   disable display of the message echo")
        print("  * ;caps     capitalize all letters")
        print("  * ;reverse  reverse the message")
        print("  * ;text     explicitly begin your message's text")

    elif "all" in cmds:
        cmds = ["help", "status", "write", "set"]
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
def cmd_status(client: Client, operands = None):
    client_state = client.get_state()
    #print(" Connection: " + (client.connection.sock is not None)*"Active" + (client.connection.sock is None)*"Closed")
    #print(" Message Buffer: " + (client.message is not None)*"Full" + (client.message is None)*"Empty")
    #print(f" Recieve Buffer: {len(client.recieved)}\n")

    #print(f"\n Logging: {client.fl_logging}")
    #print(f" Instant: {client.fl_instant}")
    #print(f" Listen: {client.fl_listen}")
    #print(f" Force: {client.fl_force}\n")

    #for flag in client.flags:
    #    print(f" {flag}: {client.flags[flag]}")

    print(f" Connection: {client_state["connection"]}")
    print(f" Host: {client_state["connectionhost"]}")
    print(f" Port: {client_state["connectionport"]}\n")

    print(f" Write Buffer: {client_state["messagebuffer"]}")
    print(f" Inbox: {client_state["recievebuffer"]}\n")

    for flag in client_state["flags"]:
        print(f"  {flag}: {client_state["flags"][flag]}")

# WRITE
# Creates a Message from string & writes it to the Client's write buffer
def cmd_write(client: Client, operands: list[str]):
    if len(operands) > 0: msg_definition_str = operands[0]
    else: msg_definition_str = ""   # allow for blank messages

    mess = Message(parse_message_data_string(msg_definition_str)) # @? should parsing the message data be done HERE or in MESSAGES?
    client.message_write(mess)

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
# Gracefully shutdown client connection, set the client kill signal
def cmd_quit(client: Client, operands = None):
    client.connection_close()
    client.killme = True

# VIEW
# View the message in buffer
def cmd_view(client: Client, operands = None):
    client.message_view()

# EDIT
# Edit the message in buffer
def cmd_edit(client: Client, operands: list[str]):
    if len(operands) > 0: msg_definition_str = operands[0]
    else: msg_definition_str = ""   # allow for empty edits

    client.message_edit(parse_message_data_string(msg_definition_str))

# =============================================================================

# ----------------------
# Command Types and Data
# ----------------------

# Types of commands in the client + associated procedures
class CommandCode(Enum):
    Null    = None
    Help    = cmd_help #0            # Help text
    Status  = cmd_status #1          # Client state
    Write   = cmd_write  #2           # Write message
    Set     = cmd_set #3             # Set a client flag
    Quit    = cmd_quit #4

    View = cmd_view #5            # View message written in buffer
    Edit = cmd_edit #6            # Edit message written in buffer


#    clear # clear message in buffer
#    edit # edit message in buffer
#    send # send message in buffer (manual)
#
# keepwrite # everything written is a message sent : text : text
#
#    read # read messages recieved
#    clear # clear messages recieved

    #quit

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
    #opcode = CommandCode.Null   # Null command
    #operands = []               # No operands
    #signature = (False, False)  # Empty signature

    # Process words of command
    cmdwords = inpt.lower().split()

    # If operands given, add them
    if len(cmdwords) > 1: operands = cmdwords[1:]
    else: operands = []

    # Set opcode and signature
    opcode = CommandCode.Null   # Default null command
    signature = 0b00            # Empty signature
    match cmdwords[0]:
        case "help":
            opcode = CommandCode.Help
            signature = 0b01
        case "status":
            opcode = CommandCode.Status
            signature = 0b10
        case "write":
            opcode = CommandCode.Write
            signature = 0b11
            # Special operand case: use single raw input string preserve text spacing
            if len(operands) > 0: operands = [inpt[6:]]
        case "set":
            opcode = CommandCode.Set
            signature = 0b11
        case "quit":
            opcode = CommandCode.Quit
            signature = 0b10
        case "view":
            opcode = CommandCode.View
            signature = 0b10
        case "edit":
            opcode = CommandCode.Edit
            signature = 0b11
            # Special operand case: use single raw input string preserve text spacing
            if len(operands) > 0: operands = [inpt[5:]]
        case _:
            print(f" ! unknown command '{inpt}'")

    return Command(opcode, operands, signature)

#if cmdwords[0] == "help"
#
#    match cmdwords[0]:
#        # HELP
#        # 0 -> n operands
#        # (0, 1) signature
#        case "help":
#            opcode = CommandCode.Help
#            if len(cmdwords) > 1: operands = cmdwords[1:]   # Add help operands (specific commands to explain)
#        # STATUS
#        # 0 operands
#        case "status":
#            opcode = CommandCode.Status
#        # WRITE
#        # 1 operand
#        case "write":
#            opcode = CommandCode.Write
#            if len(cmdwords) > 1: operands = [inpt[6:]]     # Add rest of command (message modifiers and text) 
#            else: operands = [""]                           # If only "write" was written, specify it as blank
#        # SET
#        # 2 operands
#        case "set":
#            opcode = CommandCode.Set
#            operands = ["", ""]
#            if len(cmdwords) != 3: print(f" ! bad set command, must be 3 words (set flag on/off)")
#            else: operands = [cmdwords[1], cmdwords[2]]
#        # QUIT
#        # 0 operands
#        case "quit":
#            opcode = CommandCode.Quit
#        # VIEW
#        # 0 operands
#        case "view":
#            opcode = CommandCode.View
#        # EDIT
#        # 1 operand
#        case "edit":
#            opcode = CommandCode.Edit
#            if len(cmdwords) > 1: operands = [inpt[5:]]     # Same deal as 'write' add rest of command (message modifiers and text) 
#            else: operands = [""]                           # If only "edit" was written, specify it as blank
#        # INVALID
#        # 0 operands/CommandCode.Null
#        case _:
#            print(f" ! unknown command '{inpt}'")
#
#    return Command(opcode, operands)

# COMMAND_RUN
# Executes the given command's procedure on a Client object
def command_run(client: Client, cmd: Command) -> bool:
    success = True
    print(cmd)
    print(cmd.opcode)

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
        #print(f" ! unknown command type '{cmd}'\n")
        success = False

    #match cmd.opcode:
    #    case CommandCode.Null:
    #        print(" hint: use the 'help' command")
    #    case CommandCode.Help:
    #        helpme(cmd.operands)
    #    case CommandCode.Status:
    #        status(client)
    #    case CommandCode.Write:
    #        print(cmd.operands)
    #        write(client, cmd.operands[0])
    #    case CommandCode.Set:
    #        if cmd.operands[1] == "on": setflag(client, cmd.operands[0], True)
    #        elif cmd.operands[1] == "off": setflag(client, cmd.operands[0], False)
    #        else: print(f" ! flags can only be set on or of, not '{cmd.operands[1]}'")
    #    case CommandCode.Quit:
    #        quit(client)
    #    case CommandCode.View:
    #        view(client)
    #    case CommandCode.
    #    case _:
    #        print(f" ! unknown command type '{cmd}'\n")
    #        success = False
    print() # newline between commands
    return success


