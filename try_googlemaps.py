
import streamlit as st
import sqlite3
from geopy.geocoders import Nominatim
import googlemaps
from datetime import datetime, timedelta
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim

# Set your Google Maps API key
GOOGLE_MAPS_API_KEY = 'AIzaSyB1fci-tkq5acaMq03CHA0nX539iZ6aexE'
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)



# Function to create a database connection
def create_connection():
    conn = sqlite3.connect("events.db")
    return conn

# Function to initialize the database
def init_db():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT,
            address TEXT,
            event_description TEXT,
            start_datetime TEXT,
            end_datetime TEXT,
            timezone TEXT,
            audience TEXT,
            event_type TEXT,
            business_email TEXT,
            likes INT
        )
    ''')


    conn.commit()
    conn.close()

# Function to insert an event into the database
def insert_event(data):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO events
        (business_name, address, event_description, start_datetime, end_datetime, timezone, audience, event_type, business_email, likes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)

    conn.commit()
    conn.close()

# Function to get or create session state
def get_session_state():
    session_state = st.session_state

    if not hasattr(session_state, "initialized"):
        session_state.initialized = True
        session_state.page = "home"

    return session_state

# Home page
def home_page():
    st.title("Event Platform")
    st.header("Welcome to the Home Page")

    st.subheader("Select an Option:")
    session_state = get_session_state()
    business_btn = st.button("Business")
    customer_btn = st.button("Customer")

    if business_btn:
        session_state.page = "business"

    if customer_btn:
        session_state.page = "customer"

    if session_state.page == "business":
        business_page()
    elif session_state.page == "customer":
        customer_page()


def extract_city_from_geocode(location):
    # Extract city from the address_components
    for component in location.raw.get("address_components", []):
        if "locality" in component["types"]:
            return component["long_name"]


# Business Page
def business_page():
    st.title("Business Page")
    st.header("Submit Your Event Details")

    business_name = st.text_input("Enter Business Name")
    address = st.text_input("Enter Business Address")
    # Autocomplete for address using Google Places API
    locator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
    location = locator.geocode(address, components={"country": "US"})

    if location:
        st.info(f"Selected Address: {location.address}")
        city = extract_city_from_geocode(location)
    else:
        city = st.text_input("Enter City:")


    event_description = st.text_area("Event Description")
    # image_upload = st.file_uploader("Upload Event Image", type=["jpg", "png", "jpeg"])

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date (Optional)")

    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time (Optional)")
    start_datetime = f"{start_date} {start_time}"
    end_datetime = f"{end_date} {end_time}"

    timezone = st.selectbox("Select Time Zone", ["UTC", "EST", "CST", "PST"])

    audience_options = st.multiselect("Select Audience", ["Student", "Senior Citizen", "Kids", "General"])
    event_type_options = st.multiselect("Select Event Type", ["Art", "Music", "Food", "Social", "Entertainment", "Holiday"])

    business_email = st.text_input("Business Email (not displayed on post)")
    likes = 0

    if st.button("Submit"):
        data = (
            business_name, address, event_description,
            start_datetime, end_datetime,
            timezone, ", ".join(audience_options), ", ".join(event_type_options), business_email, likes
        )

        insert_event(data)
        get_session_state().page = "home"

        st.success("Event Submitted Successfully")

# Customer Page
def customer_page():
    st.title("Customer Page")
    st.header("Discover Events Near You")

    user_location = st.text_input("Enter Your Location")
    locator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
    location = locator.geocode(user_location, components={"country": "US"})

    if location:
        st.info(f"Selected Address: {location.address}")

    if location:
        user_latitude, user_longitude = location.latitude, location.longitude
        display_posts(user_latitude, user_longitude)

# Function to fetch and display posts
def display_posts(user_latitude, user_longitude):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM events ORDER BY start_datetime DESC')
    events = cursor.fetchall()

    for event in events:
        distance = calculate_distance(user_latitude, user_longitude, event[2])
        if distance is not None and distance < 50:  # Display events within 50 km radius for example
            st.write("Business Name:", event[1])
            st.write("Event Description:", event[3])
            st.write("Distance:", f"{distance:.2f} km")

            # Use a unique identifier for the like button based on event ID
            like_button_key = f"like_button_{event[0]}"

            # Fetch current likes count
            cursor.execute('SELECT likes FROM events WHERE id = ?', (event[0],))
            current_likes = cursor.fetchone()[0]

            # Display current likes count
            st.write("Likes:", current_likes)

            # Check if the Like button is clicked
            if st.button("Like", key=like_button_key):
                update_likes(event[0])  # Update likes for the specific event

    conn.close()

# Function to update the "likes" attribute for a specific event
def update_likes(event_id):
    conn = create_connection()
    cursor = conn.cursor()

    # Fetch current likes count
    cursor.execute('SELECT likes FROM events WHERE id = ?', (event_id,))
    current_likes = cursor.fetchone()[0]

    # Update likes count
    cursor.execute('UPDATE events SET likes = ? WHERE id = ?', (current_likes + 1, event_id))

    conn.commit()
    conn.close()

# Function to calculate distance between two locations
def calculate_distance(lat1, lon1, address) -> int:
    geolocator = Nominatim(user_agent="event_platform")
    location = geolocator.geocode(address)
    if location:
        lat2, lon2 = location.latitude, location.longitude
        origin = (lat1, lon1)
        destination = (lat2, lon2)

        # Use the distance_matrix function to get distance information
        result = gmaps.distance_matrix(origin, destination)

        # Extract the distance value
        distance = result['rows'][0]['elements'][0]['distance']['value']

        # Convert distance to kilometers
        distance_in_km = distance / 1000
        return int(distance_in_km)  # Convert to kilometers

# Run the app
if __name__ == "__main__":
    init_db()
    home_page()