import socket
import threading

HOST_IP = '172.20.94.117'
HOST_PORT = 9600
ENCODER = "utf-8"
BYTESIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen(5)

# accept incoming connections
print("Server is running...\n")

# function to handle receiving messages
def receive_messages():
    while True:
        client_socket, client_address = server_socket.accept()
        message = client_socket.recv(BYTESIZE).decode()

        if message == "close":
            client_socket.send("close".encode(ENCODER))
            print("\nMessage closed")
            break
        else:
            print(f"\nCLIENT: {message}")
            client_socket.close

# function to handle sending messages
def send_messages():
    client_socket, client_address = server_socket.accept()

    while True:
        # client_socket.send("You are connected...\n".encode())
        message = input("SERVER: ")
        client_socket.send(message.encode(ENCODER))
        if message == "close":
            break
        # client_socket.close

# create two threads for sending and receiving
receive_thread = threading.Thread(target=receive_messages)
send_thread = threading.Thread(target=send_messages)

# start the threads
receive_thread.start()
send_thread.start()

# wait for both threads to finish
receive_thread.join()
send_thread.join()

server_socket.close()
