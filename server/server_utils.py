import json
import os
import hashlib
import threading
import time
import random
from Crypto.Hash import SHA256
from sconnector import send_message, receive_message

# Path to the JSON file where user data will be stored
DATA_FILE = "./user_data.json"

# Function to generate a random wait time between provided seconds in 0.1 second increments default is 0.1 to 1.3 seconds
def randomwait(lower=1, upper=13):
    time.sleep(random.randrange(lower, upper) / 10.0)  # Simulate some processing time

def load_users():
    """Load existing user data from a JSON file"""
    with threading.Lock() as loadlock:
        if (not os.path.exists(DATA_FILE)) or (os.path.getsize(DATA_FILE) == 0):
            with open(DATA_FILE, "w") as f:
                json.dump({"users": []}, f, indent=4)
        with open(DATA_FILE, "r") as f:
            return json.load(f)

def save_users(data):
    """Save user data to a JSON file"""
    # Get current data
    current_data = load_users()
    # Merge new data into/over existing data
    current_data.update(data)
    # Save the updated data to the file
    with threading.Lock() as savelock:
        with open(DATA_FILE, "w") as f:
            json.dump(current_data, f, indent=4)

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
    # print(f"Received registration data: {data}")
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
        result = create_user(
            data["name"],
            data["email"],
            data["username"],
            data["password"],
            data["key"]
        )
        send_message(ssl_client_socket, json.dumps(result))


def login_user(ssl_client_socket, data):
    required_fields = ["username", "password"]
    if any(not data.get(field) for field in required_fields):
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "Username and password are required for login."
        }))
        return

    username = data["username"]
    password = data["password"]
    hashed_password = hash_password(password)

    users = load_users()["users"]

    for user in users:
        if user["username"] == username:
            if user["password"] == hashed_password:
                user["online"] = True
                save_users({"users": users})
                send_message(ssl_client_socket, json.dumps({
                    "status": "OK",
                    "message": f"Login successful. Welcome, {username}!"
                }))
                return
            else:
                send_message(ssl_client_socket, json.dumps({
                    "status": "ERROR",
                    "message": "Incorrect password."
                }))
                return

    send_message(ssl_client_socket, json.dumps({
        "status": "ERROR",
        "message": "User does not exist."
    }))

def verify_user_credentials(username, password):
    try:
        with open(DATA_FILE, 'r') as f:
            users = json.load(f)

        if username not in users:
            return False, "User not found."

        stored_hash = users[username]["password"]
        input_hash = SHA256.new(password.encode()).hexdigest()

        if input_hash == stored_hash:
            return True, "Authenticated"
        else:
            return False, "Incorrect password."
    except Exception as e:
        return False, f"Error verifying credentials: {e}"

def set_user_online(username, status):
    try:
        with open(DATA_FILE, 'r+') as f:
            users = json.load(f)
            if username in users:
                users[username]["online"] = status
                f.seek(0)
                json.dump(users, f, indent=4)
                f.truncate()
    except Exception as e:
        print(f"Error setting user {username} online status: {e}")

# Function to handle adding friends
def add_user_friend(ssl_client_socket, data, username=None):
    # If user is not logged in, wait for 0.1 to 1.3 seconds before sending false OK message
    if not username:
        randomwait()
        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": f"{data["friend_username"]} added to friends list if registered and not in list already"
        }))
        return
    elif username == data["friend_username"]:
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": f"Cannot add self to friends list"
        }))
        return
    else:
        userdata = load_users()
        if user_exists(data["friend_username"]):
            for user in userdata["users"]:
                if user["username"] == username:
                    if data["friend_username"] not in user["friends"]:
                        user["friends"].append(data["friend_username"])
                    break
        # Save the updated user data to the JSON file
        try:
            save_users(userdata)  # Save the updated data to the file
            send_message(ssl_client_socket, json.dumps({
                "status": "OK",
                "message": f"{data["friend_username"]} added to friends list if registered and not in list already"
            }))
        except Exception as e:
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": f"Failed to add friend: {str(e)}"
            }))

# Function to handle adding friends
def remove_user_friend(ssl_client_socket, data, username=None):
    # If user is not logged in, wait for 0.7 to 1.9 seconds before sending false OK message
    if not username:
        randomwait(7, 19)
        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": f"{data['friend_username']} removed from friends list/was not in friends list"
        }))
        return
    else:
        userdata = load_users()
        # Remove friend from user's friend list if they exist, do nothing if not
        if user_exists(data["friend_username"]):
            for user in userdata["users"]:
                if user["username"] == username:
                    if data["friend_username"] in user["friends"]:
                        user["friends"].remove(data["friend_username"])
                    break
        # Save the updated user data to the JSON file
        try:
            save_users(userdata)  # Save the updated data to the file
            send_message(ssl_client_socket, json.dumps({
                "status": "OK",
                "message": f"{data['friend_username']} removed from friends list/was not in friends list"
            }))
        except Exception as e:
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": f"Failed to remove friend: {str(e)}"
            }))

# Function to show online friends
def show_online_friends(ssl_client_socket, data, username=None):
    # If user is not logged in, wait for 0.4 to 2.6 seconds before sending false OK message
    if not username:
        randomwait(4, 26)
        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": f"No Friends Online"
        }))
        return
    else:
        try:
            # Get online users
            friends = get_online_friends(load_users(), username)
            # If no friends online, notify, else return list of friends
            if not friends:
                send_message(ssl_client_socket, json.dumps({
                    "status": "OK",
                    "message": f"No Friends Online"
                }))
                return
            else:
                send_message(ssl_client_socket, json.dumps({
                    "status": "OK",
                    "message": "\n\t".join(friends)
                }))
                return
        except Exception as e:
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": f"Failed to get online friends: {str(e)}"
            }))

# Get string list of all friends within user's friendlist who are online | returns None if no friends are online
def get_online_friends(userdata, username):
    output = []
    friendlist = []
    # Get user's friendlist
    for user in userdata["users"]:
        if user["username"] == username:
            friendlist = user["friends"]

    # Go through friendlist, if user is in friend's friendlist and friend is online, add username to list and then send
    for user in userdata["users"]:
        if user["username"] in friendlist:
            if user["online"] and (username in user["friends"]):
                output.append(user["username"])
    return None if not output else output

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

