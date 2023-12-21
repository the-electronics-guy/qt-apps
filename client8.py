import socket
import threading

DESTINATION_IP = '172.20.94.117'
DESTINATION_PORT = 80
ENCODER = "utf-8"
BYTESIZE = 1024

# client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((DESTINATION_IP, DESTINATION_PORT))
client_socket.send("Connected to server...\n".encode(ENCODER))

# function to handle receiving messages
def receive_messages():
    while True:
        message = client_socket.recv(BYTESIZE).decode(ENCODER)

        if message == "close":
            print("\nChat closed...")
            break
        else:
            print(f"\nSERVER: {message}")

# function to handle sending messages
def send_messages():
    while True:
        message = input("[CLIENT]: ")
        client_socket.send(message.encode(ENCODER))
        if message == "close":
            break

# create two threads for sending and receiving
receive_thread = threading.Thread(target=receive_messages)
send_thread = threading.Thread(target=send_messages)

# start the threads
receive_thread.start()
send_thread.start()

# wait for both threads to finish
receive_thread.join()
send_thread.join()

client_socket.close()
