from client import Client
from messages import 
from enum import Enum
from dataclasses import dataclass

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
    Help = 0
    Status = 1
    Write = 2

# Command data container 
@dataclass
class Command():
    opcode: CommandCode
    operands: tuple[str]

# =============================================================================

# ------------------
# Command procedures
# ------------------

# HELP
# Prints instructions on how to use the client
def helpme():
    print("---")
    print(" Commands")
    print("  help         - Display this message")
    print("  status       - Display client state")
    print("  write        - Write a message\n")

    print(" Writing Messages")
    print("  Commands begin with ';'. Some commands are singly worded (;echo), others doubly (;spoof 'ip').")
    print("  The first occurence of a single word without the command prefix is considered the start of the text in your message.")
    print("  Commands: ;noecho | ;caps | ;reverse | ;spoof 'ip' | 'your message text here'")
    print("   Ex: ;noecho ;spoof 127.0.0.1 Hello World!")
    print("---\n")

# STATUS
# Displays the state of the client's components
def status(client: Client):
    print(" Connection: " + (client.connection.sock is not None)*"Active" + (client.connection.sock is None)*"Closed")
    print(" Message Buffer: " + (client.message is not None)*"Full" + (client.message is None)*"Empty")
    print(f" Recieve Buffer: {len(client.recieved)}")

    print(f"\n Logging: {client.fl_logging}")
    print(f" Instant: {client.fl_instant}")
    print(f" Listen: {client.fl_listen}")
    print(f" Force: {client.fl_force}\n")

# WRITE
# Lets user write a message to the client message write buffer
def write(client: Client, msg_definition_str: str):
    


    client.message_write()

# =============================================================================

# ----------------------------
# Getting and Running Commands
# ----------------------------

# COMMAND_GET
# Returns a Command dataclass interpreted from the given string (or None if no valid command found)
def command_get(inpt: str) -> Command:
    cmd = Command(None, ())
    match inpt:
        case "help":
            cmd.opcode = CommandCode.Help
        case "status":
            cmd.opcode = CommandCode.Status
        case "write":
            cmd.opcode = CommandCode.Write
        case _:
            print(f"CMDGETERR: Unkown command '{inpt}'\n")
    return cmd

# COMMAND_RUN
# Executes the given command's procedure on a Client object
def command_run(client: Client, cmd: Command):
    match cmd.opcode:
        case CommandCode.Help:
            helpme()
        case CommandCode.Status:
            status(client)
        case CommandCode.Write:
            write(client)
        case _:
            print(f"CMDRUNERR: Unkown command type '{cmd}'\n")


