import meshtastic
import meshtastic.serial_interface

interface = meshtastic.serial_interface.SerialInterface()

node_id = '!e0d04854'
#node_ids = list(interface.nodes.keys())

if node_id in interface.nodes:
    p = interface.nodes[node_id]
    position_data = p.get("position", {})
    
    latitude = position_data.get("latitude")
    longitude = position_data.get("longitude")
    altitude = position_data.get("altitude")

    if latitude is not None and longitude is not None and altitude is not None:
        print("Latitude:", latitude)
        print("Longitude:", longitude)
        print("Altitude:", altitude)
        print(str(p))
    else:
        print(f"No position information available for node with ID '{node_id}'")
else:
    print(f"Node with ID '{node_id}' not found in the mesh network.")
