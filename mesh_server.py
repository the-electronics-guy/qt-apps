import threading
import meshtastic
import meshtastic.serial_interface
from pubsub import pub

def onReceive(packet, interface):
    if packet['decoded']['text']:
        sender_id = packet['from']
        message_text = packet['decoded']['text']
        print(f"Received message from {sender_id}: {message_text}")
    else:
        print(f"Received packet with no text content: {packet}")

def onConnection(interface, topic=pub.AUTO_TOPIC):
    interface.sendText("message from desktop")

pub.subscribe(onReceive, "meshtastic.receive")
pub.subscribe(onConnection, "meshtastic.connection.established")

interface = meshtastic.serial_interface.SerialInterface()

def receive_thread():
    try:
        while True:
            # Allow time for processing incoming messages
            interface.run_forever()
    except KeyboardInterrupt:
        print("Receive thread interrupted.")

def send_thread():
    try:
        while True:
            # Check for user input to send messages
            user_input = input("Enter your message (or press Enter to skip): ")
            if user_input:
                interface.sendText(user_input)
    except KeyboardInterrupt:
        print("Send thread interrupted.")

# Create and start threads
receive_thread = threading.Thread(target=receive_thread, daemon=True)
send_thread = threading.Thread(target=send_thread, daemon=True)

receive_thread.start()
send_thread.start()

# Wait for threads to finish
receive_thread.join()
send_thread.join()
