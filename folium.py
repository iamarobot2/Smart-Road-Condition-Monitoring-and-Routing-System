import folium

def generate_map():
    # Create a base map
    m = folium.Map(location=[12.9716, 77.5946], zoom_start=15)

    # Fetch data from the database (example using SQLite)
    conn = sqlite3.connect('potholes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT latitude, longitude, severity FROM potholes")
    potholes = cursor.fetchall()
    conn.close()

    # Add markers for each pothole
    for lat, lon, severity in potholes:
        color = "green" if severity == "Low" else "orange" if severity == "Moderate" else "red"
        folium.Marker(
            location=[lat, lon],
            popup=f"Severity: {severity}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Save the map as an HTML file
    m.save("pothole_map.html")

# Example usage
generate_map()
