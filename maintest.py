from client import Client
from commands import command_get, command_run

def main():
    #print("creating client")
    #client = Client()

    #print("setting default host: 158.83.11.22 (draco1)")
    #client.connection_set_ip("158.83.11.22")  #@todo remember make the connection attribute private

    # or should we do this? 
    # command_run(Command(CommandCode.SetHost, ["158.83.11.22"])
    # command_run(Command(CommandCode.SetPort, [31800])
    # command_run(command_get("host 158.83.11.22"))
    # command_run(command_get("port 31800"))


    print("welcome message")

    client = Client()

    client.connection_set_ip("158.83.11.22")
    client.connection_set_port(31800)

    client.connection_establish()

#    run = True
#    while run:
#        cmd = None
#        while (cmd == None):
#            inp = input("> ")
#            if inp == "QUIT":
#                run = False
#                break
#            cmd = command_get(inp)
#
#        command_run(client, cmd)

    while not client.killme: command_run(client, command_get(input("> ")))

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
