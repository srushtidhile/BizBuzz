
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            location TEXT
        )
    ''')

    conn.commit()
    conn.close()

def subscribe_email(email, location):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO subscribers (email, location) VALUES (?, ?)', (email, location))
        conn.commit()
        st.success("Subscription Successful! You will receive event notifications.")
    except sqlite3.IntegrityError:
        st.warning("Email already subscribed!")

    conn.close()

def subscription_page():
    st.title("Subscription Page")
    st.header("Subscribe for Event Notifications")

    email = st.text_input("Enter Your Email")
    user_location = st.text_input("Enter Your Location")

    locator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
    location = locator.geocode(user_location, components={"country": "US"})

    if location:
        st.info(f"Selected Address: {location.address}")

        if st.button("Subscribe"):
            subscribe_email(email, location.address)
    else:
        st.warning("Invalid Location. Please enter a valid location.")


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
    # st.header("Welcome to the Home Page")
    st.set_page_config(
        page_title="BizBuzz",
        page_icon="✨",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    with open('style.css') as f:
        custom_style = f.read()
        st.markdown(f'<style>{custom_style}</style>', unsafe_allow_html=True)

    st.markdown('<div class="header">Welcome to BizBuzz!</div>', unsafe_allow_html=True)
    # st.markdown('<div class="subheader">Select an Option:</div>', unsafe_allow_html=True)

    # button_container = st.markdown('<div class="button-container">', unsafe_allow_html=True)
    business_btn, customer_btn, subscription_btn = st.sidebar.columns([1, 1, 1])
    business_btn = st.button("Business", kwargs={
        'clicked_button_ix': 1, 'n_buttons': 3
        })
    customer_btn = st.button("Customer", kwargs={
        'clicked_button_ix': 2, 'n_buttons': 3
        })
    subscription_btn = st.button("Subscription", kwargs={
        'clicked_button_ix': 3, 'n_buttons': 3
        })
    # business_btn = st.button("Business")
    # customer_btn = st.button("Customer")
    # subscription_btn = st.button("Subscription")
    
    session_state = get_session_state()
    if business_btn:
        session_state.page = "business"
    elif customer_btn:
        session_state.page = "customer"
    elif subscription_btn:
        session_state.page = "subscription"

    if session_state.page == "business":
        business_page()
    elif session_state.page == "customer":
        customer_page()
    elif session_state.page == "subscription":
        subscription_page()

    
    local_image_path = "./images/background_text.jpg"
    st.image(local_image_path, use_column_width=True)


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
    start_time = st.time_input("Start Time")
    end_date = st.date_input("End Date")
    end_time = st.time_input("End Time")
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
    st.title("Discover Events Near You!")
    # st.header("Discover Events Near You")

    user_location = st.text_input("Enter Your Location")
    locator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
    location = locator.geocode(user_location, components={"country": "US"})

    if location:
        st.info(f"Selected Address: {location.address}")

        selected_event_types = st.multiselect("Select Event Types", ["Art", "Music", "Food", "Social", "Entertainment", "Holiday"])
        selected_audience = st.multiselect("Select Audience", ["Student", "Senior Citizen", "Kids", "General"])
        user_latitude, user_longitude = location.latitude, location.longitude
    if st.button("Search"):
        display_posts(user_latitude, user_longitude, selected_event_types, selected_audience)

# Function to fetch and display posts
def display_posts(user_latitude, user_longitude, selected_event_types, selected_audience):
    conn = create_connection()
    cursor = conn.cursor()

    query = 'SELECT * FROM events WHERE datetime(end_datetime) > CURRENT_TIMESTAMP '
    # query = 'SELECT * FROM events WHERE 1 > 0 '
    params = []

    if selected_event_types:
        query += 'AND ('
        query += ' OR '.join(["event_type LIKE ?" for _ in selected_event_types])
        params.extend(['%{}%'.format(event_type) for event_type in selected_event_types])
        query = query.rstrip("OR ") + ') '


    if selected_audience:
        query += 'AND ('
        query += ' OR '.join(["audience LIKE ?" for _ in selected_audience])
        params.extend(['%{}%'.format(audience) for audience in selected_audience])
        query = query.rstrip("OR ") + ') '

    query += 'ORDER BY end_datetime ASC'

    print("Executing query:", query)
    print("With parameters:", params)

    cursor.execute(query, params)
    events = cursor.fetchall()
    cols = st.columns(3)
    col_num = -1
    for event in events:
        col_num += 1
        col_num = col_num % 3
        distance = calculate_distance(user_latitude, user_longitude, event[2])
        if distance is not None and distance < 50:  # Display events within 50 km radius for example
            with cols[col_num]:
                with st.container(border=True,):
                    st.header(event[1])
                    st.write("Event Description:", event[3])
                    st.write("Distance:", f"{distance:.2f} km")
                    st.write("📍", event[2])
                    st.write("📅", event[4], "-", event[5])
                    st.write("Audience:", event[7])
                    st.write("Event Type:", event[8])

                    # Use a unique identifier for the like button based on event ID
                    like_button_key = f"like_button_{event[0]}"

                    # Fetch current likes count
                    cursor.execute('SELECT likes FROM events WHERE id = ?', (event[0],))
                    current_likes = cursor.fetchone()[0]

                    # Display current likes count
                    st.write("Likes:", current_likes)

                    # Check if the Like button is clicked
                    if st.button("❤", key=like_button_key):
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
def calculate_distance(lat1, lon1, address) -> float:
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
        return float(distance_in_km)  # Convert to kilometers

# Run the app
if __name__ == "__main__":
    init_db()
    home_page()