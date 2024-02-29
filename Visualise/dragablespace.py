import folium

# Example nodes with latitude, longitude, and id
nodes = [
    {"id": 1, "latitude": 37.7749, "longitude": -122.4194},
    {"id": 2, "latitude": 34.0522, "longitude": -118.2437},
    {"id": 3, "latitude": 40.7128, "longitude": -74.0060},
]

# Example vehicles with latitude, longitude, id, node, and time
vehicles = [
    {"id": 101, "latitude": 37.7749, "longitude": -122.4194, "node": 1, "time": "10:00 AM"},
    {"id": 102, "latitude": 37.7749, "longitude": -122.4194, "node": 1, "time": "10:30 AM"},
    {"id": 103, "latitude": 34.0522, "longitude": -118.2437, "node": 2, "time": "11:30 AM"},
    {"id": 104, "latitude": 34.0522, "longitude": -118.2437, "node": 2, "time": "12:00 PM"},
    {"id": 105, "latitude": 40.7128, "longitude": -74.0060, "node": 3, "time": "1:45 PM"},
    {"id": 106, "latitude": 40.7128, "longitude": -74.0060, "node": 3, "time": "2:15 PM"},
]

# Calculate the mean of coordinates for centering the map
mean_latitude = sum(node["latitude"] for node in nodes) / len(nodes)
mean_longitude = sum(node["longitude"] for node in nodes) / len(nodes)

# Create a map centered around the mean of coordinates
mymap = folium.Map(location=[mean_latitude, mean_longitude], zoom_start=5)

# Add markers for each node
for node in nodes:
    folium.Marker(location=[node['latitude'], node['longitude']], popup=f"Node {node['id']}").add_to(mymap)

# Add vehicle markers at specific times
for vehicle in vehicles:
    folium.Marker(location=[vehicle['latitude'], vehicle['longitude']],
                  popup=f"Vehicle {vehicle['id']} at Node {vehicle['node']} at {vehicle['time']}").add_to(mymap)

# Save the map to an HTML file
mymap.save("interactive_map_with_multiple_vehicles.html")