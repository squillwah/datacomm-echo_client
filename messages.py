
class Message:
    # Keywords to wrap message data elements in during message transmission
    FORMAT_KEYS = {"echo" : ("|ECHOSTART|", "|ECHOEND|"),
                   "text" : ("|TEXTSTART|", "|TEXTEND|")}

    # Constructor, initializes message to default values + optional defined data 
    def __init__(self, msg_data: dict = {}):
        # Initial values
        self.echo = True
        self.text = ""

        # Parse value initialization dict
        for key in msg_data:
            bad_key = False
            match key:
                case "echo":
                    if type(msg_data[key]) == bool: self.echo = msg_data[key]
                    else: bad_key = True
                case "text":
                    if type(msg_data[key]) == str: self.text = msg_data[key]
                    else: bad_key = True
                case _:
                    print(f"Message Initialization Error: unkown setting '{key}'")
            if bad_key:
                print(f"Message Initialization Error: bad setting type '{key}'")

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
    msg = Message()
    format_string = code.decode()
    # Echo
    echo = _key_unwrap(format_string, msg.FORMAT_KEYS["echo"])
    msg.echo = echo == "True"
    # Text
    text = _key_unwrap(format_string, msg.FORMAT_KEYS["text"])
    msg.text = text
    # Return message
    return msg

