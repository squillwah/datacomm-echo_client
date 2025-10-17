
# =============================================================================
# This file defines the Message object and related procedures.
#
# Messages consist of text and message modifiers:
#  * Text is simply the string that is the message of the Message.
#  * Modifiers effect the way our client interprets and displays the Message.
#
# The procedures defined in this file allow you to:
#  1. Encode a Message to bytes (for socket transmission)
#  2. Decode a Message from bytes
#  3. Modify the data of a Message via dict
#  4. Interpret a dict of message data from a string
#  5. Get a string of the Message's text formatted according to its modifiers
#  6. Get a string describing the raw state of the Message text and modifiers
# =============================================================================

# -------
# Message
# -------

class Message:
    # Keywords to wrap message data elements in during message transmission
    FORMAT_KEYS = {"text" : ("|TEXTSTART|", "|TEXTEND|"),
                   "echo" : ("|ECHOSTART|", "|ECHOEND|"),
                   "caps" : ("|CAPSSTART|", "|CAPSEND|"),
                   "rvrs" : ("|RVRSSTART|", "|RVRSEND|")}

    # Constructor, initializes message to default values + optional defined data 
    def __init__(self, msg_data: dict = {}):
        # Initial values
        self.text = ""
        self.modifiers = {"echo":True,
                          "caps":False,
                          "rvrs":False}

        # Parse value initialization dict for alternate values
        modify_message(self, msg_data)

# =============================================================================

# --------------------------
# Encoding/Decoding Messages
# --------------------------

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
    format_string += _key_wrap(msg.text, msg.FORMAT_KEYS["text"])               # Wrap text
    for mod in msg.modifiers:
        format_string += _key_wrap(msg.modifiers[mod], msg.FORMAT_KEYS[mod])    # Wrap modifiers
    return format_string.encode()   # Return string encoded as bytes

def decode_message(code: bytes) -> Message:
    # Create message, decode string message (formatted with protocol)
    mess = Message()
    format_string = code.decode()

    msg_data = {"text":"","modifiers":{}}
    msg_data["text"] = _key_unwrap(format_string, Message.FORMAT_KEYS["text"])
    for mod in mess.modifiers:
        msg_data["modifiers"][mod] = _key_unwrap(format_string, Message.FORMAT_KEYS[mod]) == "True"    # Convert back to bool
    modify_message(mess, msg_data)

    return mess

# =============================================================================

# ---------------------------
# Modifying/Creating Messages
# ---------------------------

# Alter components of a message with a dict
def modify_message(msg: Message, msg_data: dict):
    for data in msg_data:
        if data == "text":
            #            if "text" in msg_data:
            if msg_data["text"] is not None:
                if type(msg_data["text"]) == str: msg.text = msg_data["text"]
                else: print(" ! can't modify message text, replacement not string")
        elif data == "modifiers":
            for mod in msg_data["modifiers"]:
                if mod in msg.modifiers:
                    if type(msg_data["modifiers"][mod]) == bool: msg.modifiers[mod] = msg_data["modifiers"][mod]
                    else: print(f" ! can't modify modifier {mod}, replacement not bool")
                else: print(f" ! can't modify modifier {mod}, not a valid modifier")
        else: print(f" ! can't modify message {data}, unknown component")

def parse_message_data_string(inpt: str) -> dict:
    msg_data = {"text":None, "modifiers":{}}
    mod_prefix = ';'
    words = inpt.split()
    text_index = None
    for word in words:
        if not word.startswith(mod_prefix):
            text_index = inpt.find(word)
            break
        if word == ";text":
            text_index = inpt.find(";text")+6
            break
        match word:
            case ";noecho": msg_data["modifiers"]["echo"] = False
            case ";caps": msg_data["modifiers"]["caps"] = True
            case ";reverse": msg_data["modifiers"]["rvrs"] = True
            case _: print(f" ! unknown message modifier '{word}'")
    if text_index is not None:
        if text_index < len(inpt): msg_data["text"] = inpt[text_index:]
        else: msg_data["text"] = ""
    return msg_data

# =============================================================================

# -------------------
# Displaying Messages
# -------------------

# Return string of message formatted according to its components
def stringify_message_fancy(msg: Message) -> str:
    mess = ""
    if msg.modifiers["echo"]:
        mess = msg.text
        if msg.modifiers["caps"]:
            mess = mess.upper()
        if msg.modifiers["rvrs"]:
            mess = mess[::-1]
    return mess

# Return string of message with all data laid out plainly
def stringify_message_raw(msg: Message):
    mess = f"'{msg.text}'  "
    for mod in msg.modifiers:
        mess += f"|{mod}:{msg.modifiers[mod]}"
    mess += "|"
    return mess
