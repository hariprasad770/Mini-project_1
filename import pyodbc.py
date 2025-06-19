import requests
import pyodbc
import json

# Step 1: Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/competitions.json?api_key=TDUn19qxZted5umEoH8GFezjVMuczVGPS69CsWlw"
headers = {"accept": "application/json"}

# Make the API request
response = requests.get(url, headers=headers)
data = response.json()  # Parse JSON response

# Step 2: Connect to SQL Server using pyodbc
connection_string = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=LAPTOP-1T835K9N\WINCC;'  # SQL Server's address
    'DATABASE=tennisdb;'  # Target database
    'UID=sa;'  # SQL login username
    'PWD=Harish@123;'  # SQL login password
)
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Step 3: Insert data into Competitions and Categories tables

# Extract relevant data from the JSON response
competitions = data.get("competitions", [])

for competition in competitions:
    competition_id = competition.get("id")
    competition_name = competition.get("name")
    parent_id = competition.get("parent_id")
    type = competition.get("type")
    gender = competition.get("gender")
    
    category = competition.get("category", {})
    category_id = category.get("id")
    category_name = category.get("name")

    # Insert into the Category table (if not already exists)
    cursor.execute('''
        IF NOT EXISTS (SELECT 1 FROM categories WHERE category_id = ?)
        BEGIN
            INSERT INTO categories (category_id, category_name) VALUES (?, ?)
        END
    ''', category_id, category_id, category_name)

    # Insert into the Competition table
    cursor.execute('''
        INSERT INTO competitions (competition_id, competition_name, parent_id, type, gender, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', competition_id, competition_name, parent_id, type, gender, category_id)

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Data inserted successfully.")
