from client import Client
from commands import run_command, get_command

print("running echo-client set-up script")

print("creating client")
client = Client()

#print("starting client")
#client.start()

print("setting client connection host to 158.83.11.22")
command_run(client, command_get("host 158.83.11.22"))

print("enter desired port: ")
while(not command_run(client, command_get("port " + input()))): print("try that again: ")

print("establishing connection")
command_run(client, command_get("connect"))

print("client set-up done, running input loop\n")
while not client.killme: command_run(client, command_get(input("> ")))

# client.killme signals that whatever is managing the client should end processing with it
# client.killme should really only be modified by the graceful client.shutdown() but ig in
# event of emergency it can be set manually and 'force killed'







