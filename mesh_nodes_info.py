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
                print("No position information available for this node.")

            # Print additional information
            user_info = current_node.get("user", {})
            print("Long Name:", user_info.get("longName"))
            print("Short Name:", user_info.get("shortName"))
            print("MAC Address:", user_info.get("macaddr"))
            print("Hardware Model:", user_info.get("hwModel"))

            snr = current_node.get("snr")
            last_heard = current_node.get("lastHeard")

            if snr is not None:
                print("SNR:", snr)
            if last_heard is not None:
                print("Last Heard:", last_heard)

        else:
            print(f"Node with ID '{node_id}' not found in the mesh network.")
