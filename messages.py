
class Message:
    # Keywords to wrap message data elements in during message transmission
    FORMAT_KEYS = {"echo" : ("|ECHOSTART|", "|ECHOEND|"),
                   "text" : ("|TEXTSTART|", "|TEXTEND|")}

    # Constructor, initializes message to default values + optional defined data 
    def __init__(self, msg_data: dict = {}):
        # Initial values
        self.echo = True
        self.text = ""

        # extra credit modifiers
        self.caps = False
        self.reverse = False

        # Parse value initialization dict for alternate values
        modify_message(self, msg_data)

def _key_wrap(data, key: tuple((str, str))) -> str:
    # Wrap the data element around the given keys
    return key[0] + str(data) + key[1]

def _key_unwrap(format_string: str, key: tuple((str, str))) -> str:
    # Slice & return the data element from the formatted string
    start = format_string.find(key[0]) + len(key[0])
    end = format_string.find(key[1])
    return format_string[start : end]

def encode_message(msg: Message) -> bytes:
    format_string = ""              # String to hold 'serialized' message
    format_string += _key_wrap(msg.echo, msg.FORMAT_KEYS["echo"])
    format_string += _key_wrap(msg.text, msg.FORMAT_KEYS["text"])
    return format_string.encode()   # Return string encoded as bytes

def decode_message(code: bytes) -> Message:
    # Create message, decode string message (formatted with protocol)
    msg_data = {}
    format_string = code.decode()
    # Echo
    msg_data["echo"] = _key_unwrap(format_string, Message.FORMAT_KEYS["echo"]) == "True"
    # Text
    msg_data["text"] = _key_unwrap(format_string, Message.FORMAT_KEYS["text"])
    # Return message
    return Message(msg_data)

# Alter components of a message with a dict
def modify_message(msg: Message, msg_data: dict):
    for key in msg_data:
        bad_key = False
        match key:
            case "echo":
                if type(msg_data[key]) == bool: msg.echo = msg_data[key]
                else: bad_key = True
            case "text":
                if type(msg_data[key]) == str: msg.text = msg_data[key]
                else: bad_key = True
            case _:
                print(f"Message Modification Error: unkown setting '{key}'")
        if bad_key:
            print(f"Message Modification Error: bad setting type '{key}'")

# Get dict of message components from a string
def parse_message_command(inpt: str) -> dict:
    msg_data = {}

    inpt.lstrip()           # Trim all left whitespace
    words = inpt.split()    # Split input into list of all words (using space as delimiter)

    # Go through each word and handle commands 
    # Some commands are single worded, others may be followed by additional words, 
    #  Ex: ;noecho (1 word) | ;spoof "IP" (2 words)
    #
    # Once the first word is found which is not preceeded by the command character (;)
    # (and is not a part of a 2 word command), the rest of the word list from that
    # word forward will be recombined and interpreted as the text of the message
    word = 0
    command = True
    command_char = ';'
    while (word < len(words) and command):
        if not words[word].startswith(command_char):
            command = False
            continue

        match words[word][1:]:
            case "noecho":
                msg_data["echo"] = False
            case "spoof":                   # @todo actually implement spoofing
                msg_data["spoof"] = True
                word += 1                   # @err out of bounds access error could happen
                msg_data["spoof_ip"] = words[word]  # @todo check spoof ip formatting
            case _:
                print(f"Command Parsing Error: unkown setting {words[word][1:]}")

        word += 1

    msg_data["text"] = ' '.join(words[word:])

    return msg_data

# Return string of message formatted according to its components
def message_display_fancy(msg: Message):
    mess = ""
    if msg.echo:
        mess = msg.text
        if msg.caps:
            mess = mess.capitalize()
        if msg.reverse:
            mess = mess[-1:0]
    return mess

# Return string of message with all data laid out plainly
def message_display_raw(msg: Message):
    mess = f"Text = '{msg.text}'\nEcho = {msg.echo}\nCaps = {msg.caps}\nReverse = {msg.reverse}"
    return mess
