from enum import Enum
from dataclasses import dataclass

from client import Client
from messages import Message, parse_message_command

# =============================================================================
# Here lies all commands possible with our echo client:
#
# Commands are simple structs holding a command type and any related operands.
# Command logic is defined in single functions which operate on Client objects.
# =============================================================================

# ----------------------
# Command Types and Data
# ----------------------

# Types of commands in the client
class CommandCode(Enum):
    Null = None
    Help = 0            # Help text
    Status = 1          # Client state
    Write = 2           # Write message
    Set = 3             # Set a client flag


#    view # view message in buffer
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
    opcode: CommandCode
    operands: list[str]

# =============================================================================

# ------------------
# Command procedures
# ------------------

# HELP
# Prints instructions on how to use the client
def helpme(cmds: list[str]):
    if len(cmds) == 0:
        print(" [Commands]: ")
        print("  * help")
        print("  * status")
        print("  * write")
        print("  * set\n")
        print("  Run this command with commands you want help with (or all for all commands)")
        print("  ex: 'help status' / 'help write status' / 'help all'\n")

        print(" [Writing Messages]:")
        print("  Message modifiers begin with ';'.")
        print("  The first word without the modifier prefix is considered the start of your message.")
        print("  (if your message must start with a ';', use ;text to begin your message)")
        print("  modifiers: ;noecho | ;caps | ;reverse | ;text yourmessagehere")
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
            case _:
                print(f" ! can't help you with '{cmd}'")

# STATUS
# Displays the state of the client's components
def status(client: Client):
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
    print(f" Write Buffer: {client_state["messagebuffer"]}")
    print(f" Inbox: {client_state["recievebuffer"]}\n")

    for flag in client_state["flags"]:
        print(f"  {flag}: {client_state["flags"][flag]}")

# WRITE
# Creates a Message from string & writes it to the Client's write buffer
def write(client: Client, msg_definition_str: str):
    mess = Message(parse_message_command(msg_definition_str)) # @? should parsing the message data be done HERE or in MESSAGES?
    client.message_write(mess)

# SET
# Toggle parts of the client on/off
def setflag(client: Client, flag: str, onoff: bool):
    if flag in client.flags:
        client.flags[flag] = onoff
        print(f" {flag}: {client.flags[flag]}")
    else: print(f" ! unknown client setting '{flag}'")

# =============================================================================

# ----------------------------
# Getting and Running Commands
# ----------------------------

# COMMAND_GET
# Returns a Command dataclass interpreted from the given string
def command_get(inpt: str) -> Command:
    cmd = Command(CommandCode.Null, [])
    cmdwords = inpt.lower().split()
    match cmdwords[0]:
        # 0 -> n operands
        case "help":
            cmd.opcode = CommandCode.Help
            if len(cmdwords) > 1: cmd.operands = cmdwords[1:]   # Add help operands (specific commands to explain)
        # 0 operands
        case "status":
            cmd.opcode = CommandCode.Status
        # 1 operand
        case "write":
            cmd.opcode = CommandCode.Write
            if len(cmdwords) > 1: cmd.operands = [inpt[6:]]     # Add rest of command (message modifiers and text) 
            else: cmd.operands = [""]                           # If only "write" was written, specify it as blank
        # 2 operands
        case "set":
            cmd.opcode = CommandCode.Set
            cmd.operands = ["", ""]
            if len(cmdwords) != 3: print(f" ! bad set command, must be 3 words (set flag on/off")
            else: cmd.operands = [cmdwords[1], cmdwords[2]]
        case _:
            print(f" ! unknown command '{inpt}'")
    return cmd

# COMMAND_RUN
# Executes the given command's procedure on a Client object
def command_run(client: Client, cmd: Command):
    match cmd.opcode:
        case CommandCode.Null:
            print(" hint: use the 'help' command")
        case CommandCode.Help:
            helpme(cmd.operands)
        case CommandCode.Status:
            status(client)
        case CommandCode.Write:
            print(cmd.operands)
            write(client, cmd.operands[0])
        case CommandCode.Set:
            if cmd.operands[1] == "on": setflag(client, cmd.operands[0], True)
            elif cmd.operands[1] == "off": setflag(client, cmd.operands[0], False)
            else: print(f" ! flags can only be set on or of, not '{cmd.operands[1]}'")
        case _:
            print(f" ! unknown command type '{cmd}'\n")
    print() # newline between commands


