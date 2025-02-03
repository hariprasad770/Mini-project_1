import requests
import pyodbc
import json

# Step 1: Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/complexes.json?api_key=TDUn19qxZted5umEoH8GFezjVMuczVGPS69CsWlw"
headers = {"accept": "application/json"}

# Make the API request
response = requests.get(url, headers=headers)
data = response.json()  # Parse JSON response

# Step 2: Connect to SQL Server using pyodbc
connection_string = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=LAPTOP-1T835K9N\WINCC;'  # Change to your SQL Server's address or instance name
    'DATABASE=tennisdb;'  # Change to your target database
    'UID=sa;'  # SQL login username (or remove for Windows Authentication)
    'PWD=Harish@123;'  # SQL login password (or remove for Windows Authentication)
)
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Step 3: Insert data into Complexes and Venues tables

# Extract relevant data from the JSON response
complexes = data.get("complexes", [])

for complex in complexes:
    complex_id = complex.get("id")
    complex_name = complex.get("name")

    # Handle venues as a list
    venues = complex.get("venues", [])
    for venue in venues:
        venue_id = venue.get("id")
        venue_name = venue.get("name")
        city_name = venue.get("city_name")
        country_name = venue.get("country_name")
        country_code = venue.get("country_code")
        timezone = venue.get("timezone")

        # Insert into the Complexes table (if not already exists)
        cursor.execute('''
            IF NOT EXISTS (SELECT 1 FROM complexes WHERE complex_id = ?)
            BEGIN
                INSERT INTO complexes (complex_id, complex_name) VALUES (?, ?)
            END
        ''', complex_id, complex_id, complex_name)

        # Insert into the Venues table (if not already exists)
        cursor.execute('''
           
                INSERT INTO venues (venue_id, venue_name, city_name, country_name, country_code, timezone, complex_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', venue_id, venue_name, city_name, country_name, country_code, timezone, complex_id)

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Data inserted successfully.")

