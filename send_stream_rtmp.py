import socket
import cv2
import pickle
import struct

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()

print("host name", host_name)
host_ip = 'localhost'
print('HOST IP:', host_ip)
port = 9999

socket_address = (host_ip, port)
server_socket.bind(socket_address)
server_socket.listen()
print("LISTENING AT:", socket_address)

try:
    while True:
        client_socket, addr = server_socket.accept()
        print('GOT CONNECTION FROM:', addr)
        if client_socket:
            vid = cv2.VideoCapture('rtsp://10.81.238.189:8554/')
            #vid = cv2.VideoCapture(0)

            while(vid.isOpened()):
                img, frame = vid.read()
                a = pickle.dumps(frame)
                message = struct.pack("Q", len(a)) + a
                client_socket.sendall(message)

                cv2.imshow('TRANSMITTING VIDEO', frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    client_socket.close()
except Exception as e:
    print("Could not display")
