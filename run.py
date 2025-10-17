from client import Client
from commands import command_get, command_run

print(" .running client setup script:")

print(" .creating client")
client = Client()

print(" .setting host to draco1 with 'host 158.83.11.22'")
command_run(client, command_get("host 158.83.11.22"))

while(not command_run(client, command_get("port " + input(" .asking you for initial port: ")))): pass

print(" .establishing connection with 'connect'")
command_run(client, command_get("connect"))

print(" .client setup complete, running input loop:")
print(" .try 'help' for a list of commands\n")

try:
    while not client.killme: command_run(client, command_get(input("> ")))
except:
    print(" .an unhandled error occured, attempting graceful shutdown")
    client.shutdown()


