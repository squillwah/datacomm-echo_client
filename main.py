import messages

def command_parser(inpt: str) -> dict:
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
                word += 1
                msg_data["spoof_ip"] = words[word]  # @todo check spoof ip formatting
            case _:
                print(f"Command Parsing Error: unkown setting {words[word][1:]}")

        word += 1

    msg_data["text"] = ' '.join(words[word:])

    return msg_data

def main() -> int:
    print("Commands begin with ';'. Some commands are singly worded (;echo), others doubly (;spoof 'ip').")
    print("The first occurence of a single word without the command prefix is considered the start of the text in your message.\n")
    print("Commands: ;noecho | ;spoof 'ip' | 'your message text here'")
    print("Ex: ;noecho ;spoof 127.0.0.1 Hello World!\n")

    inpt = input("Speak: ")
    parsed = command_parser(inpt)

    mess = messages.Message(parsed)

    encoded = messages.encode_message(mess)
    print(f"\n{encoded}\n")

    decoded = messages.decode_message(encoded)
    print(f"echo:{decoded.echo}")
    print(f"text:{decoded.text}\n")

    return 0

if __name__ == "__main__":
    main()





