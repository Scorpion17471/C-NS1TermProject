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

def create_user(name, email, username, password, key):
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
        "key": key,
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
    required_fields = ["name", "email", "username", "password", "key"]
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
            data["password"],
            data["key"]
        )
        send_message(ssl_client_socket, json.dumps(result))
def get_user_key(ssl_client_socket, data):
    print(f"Received request for public key")
    name = data["username"]
    print(f"username to find: '{name}'")
    with open(DATA_FILE, 'r') as keystore:     # Open JSON file of accounts
        try:
            user_data = json.load(keystore)
            user_list = user_data.get("users")  # Iterate through "users"
            if isinstance(user_list, list):
                for user in user_list:
                    if isinstance(user, dict) and user.get("username") == name: #find matching user, copy and send public key 
                        public_key = user.get("key")
                        send_message(ssl_client_socket, json.dumps({"key": public_key}))
        except Exception as e:
            print(f"Error retrieving user key")
            send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "Error retrieving public key"
        }))
# Process and save client uploaded files
def upload_file(ssl_client_socket, data):
    base_dir = './server/files/'
    os.makedirs(base_dir, exist_ok=1) # Ensure directory is available to store client files
    print("Server converted to JSON, JSON file: \n\n")
    print(data)
    # Get file name
    file = data["file"]
    file_name = file+".json"
    print(f"File name {file_name}")
    filepath = os.path.join(base_dir, file_name)
    if not file or not isinstance(file, str):
             raise ValueError("Missing or invalid 'file' name in received data.")
    print(f"Attempting to open '{file}'")
    data = json.dumps(data)
    try:
        with open(filepath, 'w') as f:
            f.write(data)  # Saving the uploaded file to server storage
            send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": "Server successfully uploaded file"
        }))
    except IOError as e:
        print(f"IO Error writing message file {file}: {e}")
    except Exception as e:
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "ERROR uploading file"
            }))


# Function for user to save a public key to their account
def save_public_key(user_data):
    name = user_data["name"]
    key = user_data["key"]
    data = []
    # Find user and write key to file
    print(f"Storing public key to record")
    try:
        with open(DATA_FILE, "r+") as jsonfileR:
            data = json.load(jsonfileR)
            for user in data:
                if isinstance(user, dict) and user.get("name") == name:
                    user["key"] = key
                    break
    except Exception as e:
        print(f"Error opening record: '{e}'")
    try:
        with open(DATA_FILE, "w") as jsonfileW:
            json.dump(data, jsonfileW, indent=3)
            print(f"Public key processed for '{name}")
    except Exception as e:
        print(f"Error saving updated record: '{e}")

