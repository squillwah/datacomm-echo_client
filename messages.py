
class Message:
    format_keys = {"echo" : ("ECHOSTART", "ECHOEND"),
                   "text" : ("TEXTSTART", "TEXTEND")}

    def __init__(self):
        self.echo = False
        self.text = ""

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
    format_string += _key_wrap(msg.echo, msg.format_keys["echo"])
    format_string += _key_wrap(msg.text, msg.format_keys["text"])
    return format_string.encode()   # Return string encoded as bytes


def decode_message(code: bytes) -> Message:
    # Create message, decode string message (formatted with protocol)
    msg = Message()
    format_string = code.decode()
    # Echo
    echo = _key_unwrap(format_string, msg.format_keys["echo"])
    msg.echo = bool(echo)
    # Text
    text = _key_unwrap(format_string, msg.format_keys["text"])
    msg.text = text
    # Return message
    return msg

