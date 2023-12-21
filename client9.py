import socket
import threading
import os

def receive_file():
    file_name = client_socket.recv(1024).decode()
    print(f"Receiving file: {file_name}")

    file_size_bytes = client_socket.recv(4)
    file_size = int.from_bytes(file_size_bytes, byteorder='big')
    print(f"File size: {file_size} bytes")

    file = open(file_name, "wb")
    received_size = 0

    while received_size < file_size:
        data = client_socket.recv(1024)
        received_size += len(data)
        file.write(data)

    file.close()
    print(f"File received: {file_name}")

def send_file(file_path):
    file_name = file_path.split("/")[-1]
    client_socket.send(file_name.encode())

    file_size = os.path.getsize(file_path)
    client_socket.send(file_size.to_bytes(4, byteorder='big'))

    with open(file_path, "rb") as file:
        for data in iter(lambda: file.read(1024), b""):
            client_socket.sendall(data)

    print(f"File sent: {file_name}")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 8080))
client_socket.send("Connected to Server...\n".encode(ENCODER))

# Example: You can start a thread to receive a file while sending another file
receive_thread = threading.Thread(target=receive_file)
receive_thread.start()

# Example: You can start another thread to send a file while receiving another file
send_thread = threading.Thread(target=send_file, args=('radios.xlsx',))
send_thread.start()

# Wait for both threads to finish
receive_thread.join()
send_thread.join()

client_socket.close()
