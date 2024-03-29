
import streamlit as st
import sqlite3
from geopy.geocoders import Nominatim
import googlemaps
from datetime import datetime, timedelta
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim
from dotenv import load_dotenv
import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *

load_dotenv()

# Set your SendGrid API key
SENDGRID_API_KEY = os.getenv('SENDGRID_KEY')

# Set your Google Maps API key
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_KEY')
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
            location TEXT,
            subscriber_latitude FLOAT,
            subscriber_longitude FLOAT
        )
    ''')

    conn.commit()
    conn.close()

def subscribe_email(email, location, subscriber_latitude, subscriber_longitude):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('INSERT INTO subscribers (email, location, subscriber_latitude, subscriber_longitude) VALUES (?, ?, ?, ?)', (email, location, subscriber_latitude, subscriber_longitude))
        conn.commit()
        st.success("Subscription Successful! You will receive event notifications.")
    except sqlite3.IntegrityError:
        st.warning("Email already subscribed!")

    conn.close()

def unsubscribe_email(email):
    conn = create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM subscribers WHERE email = ?', (email,))
        if cursor.rowcount > 0:
            conn.commit()
            st.success("Unsubscription Successful! You will no longer receive event notifications.")
        else:
            st.warning("Email not found for unsubscription.")
    except sqlite3.Error as e:
        print(f"Error during unsubscribe operation: {e}")
        st.error("An error occurred during unsubscription.")

def subscription_page():
    st.title("Subscribe for Event Notifications!")
    # st.header("Subscribe for Event Notifications")

    email = st.text_input("Your Email")
    user_location = st.text_input("Your Location (after typing, hit enter)")

    locator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
    location = locator.geocode(user_location, components={"country": "US"})

    if location:
        st.info(f"Selected Address: {location.address}")
        subscriber_latitude, subscriber_longitude = location.latitude, location.longitude

        if st.button("$subscribe$"):
            subscribe_email(email, location.address, subscriber_latitude, subscriber_longitude)
        if st.button("$unsubscribe$"):
            unsubscribe_email(email)
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

    sendgrid_api(data)

    conn.commit()
    conn.close()

def sendgrid_api(event_data):
    # Initialize SendGrid client
    sg = SendGridAPIClient(SENDGRID_API_KEY)

    print('entered sendgrid function')

    # Fetch subscribers within 50 km of the event address
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subscribers')
    subscribers = cursor.fetchall()

    for subscriber in subscribers:
        subscriber_email = subscriber[1]

        # Compose the message
        message = f"<strong>{event_data[0]}:</strong><br>Event Description: <em>{event_data[2]}</em><br>📍{event_data[1]}<br>📅 {event_data[3]}-{event_data[4]}<br>Audience: {event_data[6]}<br>Event Type: {event_data[7]}"
        from_email = Email("srd130@pitt.edu")
        to_emails = To(str(subscriber_email))
        subject = "BizBuzz: Event Near You!"

        # Create Mail object
        mail = Mail(
            from_email, to_emails, subject, html_content=message
        )

        # Send the email
        response = sg.send(mail)
        
        # Check if the email was sent successfully
        if response.status_code == 202:
            print('Email sent successfully!')
        else:
            st.error('Failed to send email. Check your API key and try again.')
                
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

    # st.markdown('<div class="header">Welcome to BizBuzz!</div>', unsafe_allow_html=True)
    welcome_image = "./images/welcome.png"
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    st.image(welcome_image, use_column_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    # st.markdown('<div class="subheader">Select an Option:</div>', unsafe_allow_html=True)

    # button_container = st.markdown('<div class="button-container">', unsafe_allow_html=True)
    cols = st.columns(3)
    with cols[0]:
        with st.container(border=False, height=100):
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            business_btn = st.button("$business$",use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    with cols[1]:
        with st.container(border=False, height=100):
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            customer_btn = st.button("$customer$",use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    with cols[2]:
        with st.container(border=False, height=100):
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            subscription_btn = st.button("$subscription$",use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
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

    
    local_image_path = "./images/author.png"
    st.image(local_image_path, use_column_width=True)


def extract_city_from_geocode(location):
    # Extract city from the address_components
    for component in location.raw.get("address_components", []):
        if "locality" in component["types"]:
            return component["long_name"]


# Business Page
def business_page():
    st.title("Submit Your Event Details!")
    # st.header("Submit Your Event Details")

    business_name = st.text_input("Business Name")
    address = st.text_input("Business Address (after typing, hit enter)")
    # Autocomplete for address using Google Places API
    locator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
    location = locator.geocode(address, components={"country": "US"})

    if location:
        st.info(f"Selected Address: {location.address}")
        city = extract_city_from_geocode(location)
    else:
        city = st.text_input("City:")


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

    if st.button("$submit$"):
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

    user_location = st.text_input("Your Location (after typing, hit enter)")
    locator = GoogleV3(api_key=GOOGLE_MAPS_API_KEY)
    location = locator.geocode(user_location, components={"country": "US"})

    if location:
        st.info(f"Selected Address: {location.address}")

        selected_event_types = st.multiselect("Select Event Types", ["Art", "Music", "Food", "Social", "Entertainment", "Holiday"])
        selected_audience = st.multiselect("Select Audience", ["Student", "Senior Citizen", "Kids", "General"])
        user_latitude, user_longitude = location.latitude, location.longitude
    if st.button("$search$"):
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
                    st.button("❤", key=like_button_key, on_click=lambda e=event[0]: update_likes(e))
                        # update_likes(event[0])  # Update likes for the specific event

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
    # print(event_id, "likes updated to", current_likes + 1)

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