import meshtastic
import meshtastic.serial_interface

interface = meshtastic.serial_interface.SerialInterface()

# Retrieve a list of available nodes and their IDs
node_ids = list(interface.nodes.keys())
print("Available node IDs:", node_ids)

# Now you can choose a valid node ID from the list and access its information
