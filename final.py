import streamlit as st
import pandas as pd
import pyodbc

# Database connection
def get_connection():
    server = "LAPTOP-1T835K9N\WINCC"
    database = "tennisdb"
    username = "sa"
    password = "Harish@123"
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    return conn

# Title and Sidebar
st.title("Tennis Analytics Dashboard")
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Select a Page", ["Homepage", "Competitor Analysis", "Venues & Complexes", "Leaderboards", "Country Analysis"])

# Homepage
if menu == "Homepage":
    st.header("Overview")
    conn = get_connection()
    cursor = conn.cursor()

    # Total competitors
    cursor.execute("SELECT COUNT(*) FROM Competitors")
    total_competitors = cursor.fetchone()[0]
    st.metric("Total Competitors", total_competitors)

    # Total countries
    cursor.execute("SELECT COUNT(DISTINCT country) FROM Competitors")
    total_countries = cursor.fetchone()[0]
    st.metric("Total Countries", total_countries)

    # Highest points
    cursor.execute("""
        SELECT TOP 1 rank, competitor_id, points
        FROM Competitor_Rankings
        ORDER BY points DESC
    """)
    top_competitor = cursor.fetchone()
    st.metric("Top Competitor(Rank,ID,Points)", f"{top_competitor[0]}, {top_competitor[1]}, ({top_competitor[2]} points)")

    conn.close()

# Competitor Analysis
elif menu == "Competitor Analysis":
    st.header("Competitor Analysis")
    conn = get_connection()

    # Search and filter competitors
    search_name = st.text_input("Search Competitor by Name")
    rank_range = st.slider("Select Rank Range", 1, 1000, (1, 100))
    query = f"""
        SELECT name, rank, points, country
        FROM Competitors
        INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
        WHERE rank BETWEEN {rank_range[0]} AND {rank_range[1]}
    """
    if search_name:
        query += f" AND name LIKE '%{search_name}%'"
    competitors = pd.read_sql(query, conn)
    st.dataframe(competitors)
    conn.close()

# Venues and Complexes
elif menu == "Venues & Complexes":
    st.header("Venues & Complexes")
    conn = get_connection()
    
    # List venues with complexes
    query = """
        SELECT Venues.venue_name, Complexes.complex_name, Venues.city_name, Venues.country_name
        FROM Venues
        INNER JOIN Complexes ON Venues.complex_id = Complexes.complex_id
    """
    venues = pd.read_sql(query, conn)
    st.dataframe(venues)

    # Venue count per complex
    query = """
        SELECT Complexes.complex_name, COUNT(Venues.venue_name) AS venue_count
        FROM Venues
        INNER JOIN Complexes ON Venues.complex_id = Complexes.complex_id
        GROUP BY Complexes.complex_name
    """
    venue_counts = pd.read_sql(query, conn)
    st.bar_chart(venue_counts.set_index("complex_name"))
    conn.close()

# Leaderboards
elif menu == "Leaderboards":
    st.header("Leaderboards")
    conn = get_connection()

    # Top-ranked competitors
    query = """
        SELECT TOP 10 rank_id, rank, points, competitions_played
        FROM Competitor_Rankings
        ORDER BY rank ASC
    """
    top_ranks = pd.read_sql(query, conn)
    st.subheader("Top-Ranked Competitors")
    st.dataframe(top_ranks)

    # Competitors with highest points
    query = """
        SELECT TOP 10 rank_id, rank, points, competitions_played
        FROM Competitor_Rankings
        ORDER BY points DESC
    """
    top_points = pd.read_sql(query, conn)
    st.subheader("Competitors with Highest Points")
    st.dataframe(top_points)

    conn.close()

# Country Analysis
elif menu == "Country Analysis":
    st.header("Country-Wise Analysis")
    conn = get_connection()

    # Competitors by country
    query = """
        SELECT country, COUNT(*) AS total_competitors, AVG(points) AS avg_points
        FROM Competitors
        INNER JOIN Competitor_Rankings ON Competitors.competitor_id = Competitor_Rankings.competitor_id
        GROUP BY country
        ORDER BY total_competitors DESC
    """
    country_analysis = pd.read_sql(query, conn)
    st.bar_chart(country_analysis.set_index("country"))

    conn.close()
