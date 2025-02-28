import sqlite3

def save_to_database(lat, lon, severity):
    conn = sqlite3.connect('potholes.db')
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO potholes (latitude, longitude, severity)
        VALUES (?, ?, ?)
    """, (lat, lon, severity))
    conn.commit()
    conn.close()

# Example usage
save_to_database(12.9716, 77.5946, "High")
