from client import Client
from commands import command_get, command_run

print("running echo-client set-up script")

print("creating client")
client = Client()

#print("starting client")
#client.start()

print("setting client connection host to 158.83.11.22")
command_run(client, command_get("host 158.83.11.22"))

# @todo fix this input check not working
while(not command_run(client, command_get("port " + input("enter port: ")))): pass

print("establishing connection")
command_run(client, command_get("connect"))

print("client set-up done, running input loop")
print("try 'help' for a list of commands\n")
try:
    while not client.killme: command_run(client, command_get(input("> ")))
except:
    print("an unhandled error occured, shutting down gracefully")
    client.shutdown()


