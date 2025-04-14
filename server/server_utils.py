import json
import os
import hashlib

from sconnector import send_message, receive_message

# Path to the JSON file where user data will be stored
DATA_FILE = "./user_data.json"

def load_users():
    """Load existing user data from a JSON file"""
    if not os.path.exists(DATA_FILE):
        return {"users": []}  # If file doesn't exist, return empty data
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    """Save user data to a JSON file"""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    """Hash password using SHA-256 for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username):
    """Check if a user with the given username already exists"""
    users = load_users()["users"]
    return any(user["username"] == username for user in users)

def create_user(name, email, username, password):
    """Create a new user account and store it in the JSON file"""
    if user_exists(username):
        return {"status": "ERROR", "message": "Username is already taken."}
    
    user = {
        "name": name,
        "email": email,
        "username": username,
        "password": hash_password(password),  # Store hashed password
        "online": False,  # New users are offline by default
        "friends": [],  # New users have no friends by default
    }
    
    data = load_users()
    data["users"].append(user)
    
    try:
        save_users(data)  # Save the updated data to the file
        return {"status": "OK", "message": "Registration successful"}
    except Exception as e:
        return {"status": "ERROR", "message": f"Failed to create user account: {str(e)}"}

# Function takes in SSL socket and data from client, checks if all required fields are present, then calls create_user function to create a new user account.
def register_user(ssl_client_socket, data):
    print(f"Received registration data: {data}")
    # Check if all required fields are present and valid
    required_fields = ["name", "email", "username", "password"]
    if any(not data[field] for field in required_fields):
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "All fields must be filled."
        }))
    elif (len(data["password"]) < 16) or (not data["password"].isalnum()):
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "Password must be at least 16 characters long and contain only both letters and numbers."
        }))
    # If all validation checks pass, call create_user function
    else:
        print(f"name: {data['name']}, email: {data['email']}, username: {data['username']}, password: {data['password']}")
        result = create_user(
            data["name"],
            data["email"],
            data["username"],
            data["password"]
        )
        send_message(ssl_client_socket, json.dumps(result))