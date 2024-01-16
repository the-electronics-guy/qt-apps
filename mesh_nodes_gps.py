import meshtastic
import meshtastic.serial_interface

interface = meshtastic.serial_interface.SerialInterface()

# Retrieve a list of available nodes and their IDs
node_ids = list(interface.nodes.keys())
print("Available node IDs:", node_ids)

# Check if there are any nodes in the network
if not node_ids:
    print("No nodes found in the mesh network.")
else:
    # Iterate through all available nodes
    for node_id in node_ids:
        if node_id in interface.nodes:
            current_node = interface.nodes[node_id]
            position_data = current_node.get("position", {})

            latitude = position_data.get("latitude")
            longitude = position_data.get("longitude")
            altitude = position_data.get("altitude")

            print(f"\nNode ID: {node_id}")
            if latitude is not None and longitude is not None and altitude is not None:
                print("Latitude:", latitude)
                print("Longitude:", longitude)
                print("Altitude:", altitude)
            else:
                print(f"No position information available for this node.")
            print(str(current_node))
        else:
            print(f"Node with ID '{node_id}' not found in the mesh network.")
