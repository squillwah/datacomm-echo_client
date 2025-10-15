from client import Client
from commands import command_get, command_run

def main():
    print("welcome message")

    client = Client()

    client.connection_set_ip("158.83.11.22")
    client.connection_set_port(31800)

    client.connection_establish()

    run = True
    while run:
        cmd = None
        while (cmd == None):
            inp = input()
            if inp == "QUIT":
                run = False
                break
            cmd = command_get(inp)

        command_run(client, cmd)

    #command_execute(client, command_interpret(inp))

#    print(client.recieved[0].text)
#    print(client.recieved[0].echo)

    client.connection_close()


    print()
    print()

#    m = Message(parse_message_command("noecho testtesttest"))
#
#    print(message_display_raw(m))
#    print(message_display_fancy(m))

    print("hello")

main()
