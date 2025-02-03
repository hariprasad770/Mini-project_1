import requests
import pyodbc
import json

# Step 1: Fetch data from the API
url = "https://api.sportradar.com/tennis/trial/v3/en/double_competitors_rankings.json?api_key=TDUn19qxZted5umEoH8GFezjVMuczVGPS69CsWlw"
headers = {"accept": "application/json"}

# Make the API request
response = requests.get(url, headers=headers)
data = response.json()  # Parse JSON response

# Step 2: Connect to SQL Server using pyodbc
connection_string = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=LAPTOP-1T835K9N\\WINCC;'  # Change to your SQL Server's address or instance name
    'DATABASE=tennisdb;'  # Change to your target database
    'UID=sa;'  # SQL login username
    'PWD=Harish@123;'  # SQL login password
)
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# Step 3: Insert data into Competitor Rankings and Competitors tables

# Extract rankings from the JSON response
rankings = data.get("rankings", [])

for ranking in rankings:
    competitor_rankings = ranking.get("competitor_rankings", [])

    for competitor_ranking in competitor_rankings:
        rank = competitor_ranking.get("rank")
        movement = competitor_ranking.get("movement")
        points = competitor_ranking.get("points")
        competitions_played = competitor_ranking.get("competitions_played")
        competitor = competitor_ranking.get("competitor", {})

        # Extract competitor fields with default values for missing ones
        competitor_id = competitor.get("id")
        competitor_name = competitor.get("name", "Unknown")  # Default name if missing
        country = competitor.get("country", "Unknown")  # Default country if missing
        country_code = competitor.get("country_code", "XXX")  # Default country code if missing
        abbreviation = competitor.get("abbreviation", "UNK")  # Default abbreviation if missing

        # Insert into Competitors table (if not already exists)
        cursor.execute('''
            IF NOT EXISTS (SELECT 1 FROM competitors WHERE competitor_id = ?)
            BEGIN
                INSERT INTO competitors (competitor_id, name, country, country_code, abbreviation)
                VALUES (?, ?, ?, ?, ?)
            END
        ''', competitor_id, competitor_id, competitor_name, country, country_code, abbreviation)

        # Insert into Competitor Rankings table
        cursor.execute('''
            INSERT INTO competitor_rankings (rank, movement, points, competitions_played, competitor_id)
            VALUES (?, ?, ?, ?, ?)
        ''', rank, movement, points, competitions_played, competitor_id)

# Commit the transaction and close the connection
conn.commit()
conn.close()

print("Data inserted successfully.")
