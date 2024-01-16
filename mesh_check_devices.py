import meshtastic.serial_interface
from pubsub import pub

def on_receive(packet, interface):
    # Print the ID of the sender node for each received packet
    sender_id = packet['from']
    print(f"Node ID: {sender_id}")

def on_connection(interface, topic=pub.AUTO_TOPIC):
    print("Connected to Meshtastic device")

# Subscribe to receive events and connection events
pub.subscribe(on_receive, "meshtastic.receive")
pub.subscribe(on_connection, "meshtastic.connection.established")

# By default, Meshtastic will try to find a device. You can provide a device path if needed.
interface = meshtastic.serial_interface.SerialInterface()

try:
    while True:
        # Allow time for processing incoming messages
        interface.receive()
except KeyboardInterrupt:
    print("Script interrupted.")
