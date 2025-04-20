import json
import os
import hashlib

# Path to the JSON file where user data will be stored
DATA_FILE = "user_data.json"

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
        return {"status": "USERNAME_TAKEN", "message": "Username is already taken."}
    
    user = {
        "name": name,
        "email": email,
        "username": username,
        "password": hash_password(password)
    }
    
    data = load_users()
    data["users"].append(user)
    
    try:
        save_users(data)  # Save the updated data to the file
        return {"status": "OK", "message": "Registration successful"}
    except Exception as e:
        return {"status": "ERROR", "message": f"Failed to create user account: {str(e)}"}

def validate_login(username, password):
    """Validate user login by checking username and hashed password"""
    users = load_users()["users"]
    hashed_password = hash_password(password)

    for user in users:
        if user["username"] == username and user["password"] == hashed_password:
            return {"status": "OK", "message": "Login successful."}
    
    return {"status": "INVALID_CREDENTIALS", "message": "Invalid username or password."}

