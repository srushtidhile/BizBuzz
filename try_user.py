import streamlit as st
import sqlite3
from hashlib import sha256

# Create SQLite database connection
conn = sqlite3.connect('user_data.db')
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        email TEXT,
        password TEXT,
        role TEXT
    )
''')
conn.commit()

# Function to hash password
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Function to register a new user
def register_user(email, password, role):
    hashed_password = hash_password(password)
    cursor.execute('''
        INSERT INTO users (email, password, role)
        VALUES (?, ?, ?)
    ''', (email, hashed_password, role))
    conn.commit()

# Function to check login credentials
def check_login(email, password, role):
    hashed_password = hash_password(password)
    cursor.execute('''
        SELECT * FROM users
        WHERE email=? AND password=? AND role=?
    ''', (email, hashed_password, role))
    return cursor.fetchone() is not None

# Main Streamlit App
def main():
    st.title("Streamlit Auth App")

    # Sidebar for role selection
    role = st.sidebar.radio("Select Role", ["Home", "Customer", "Business"])

    if role == "Home":
        st.subheader("Welcome to the Auth App!")
        st.write("Please select your role on the sidebar.")

    elif role == "Customer" or role == "Business":
        st.subheader(f"{role} Login")

        email = st.text_input("Email:")
        password = st.text_input("Password:", type="password")

        if st.button("Login"):
            if check_login(email, password, role):
                st.success(f"Login successful as {role}!")
            else:
                st.error("Invalid credentials. Please register if you are a new user.")
                if st.button("Register"):
                    register_user(email, password, role)
                    st.success(f"Registration successful as {role}!")

# Run the Streamlit App
if __name__ == "__main__":
    main()

# Close SQLite connection
conn.close()
