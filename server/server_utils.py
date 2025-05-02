import json
import os
import hashlib
import threading
import time
import random
import bcrypt
from Crypto.Hash import SHA256
from sconnector import send_message, receive_message

# Path to the JSON file where user data will be stored
#file_dir = os.path.dirname(os.path.abspath(__file__))
#DATA_FILE = os.path.join(file_dir, "user_data.json")
DATA_FILE = "./user_data.json"

# Function to generate a random wait time between provided seconds in 0.1 second increments default is 0.1 to 1.3 seconds
def randomwait(lower=1, upper=13):
    time.sleep(random.randrange(lower, upper) / 10.0)  # Simulate some processing time

def load_users():
    """Load existing user data from a JSON file"""
    with threading.Lock() as loadlock:
        if not os.path.exists(DATA_FILE) or open(DATA_FILE, "r").read() == "":
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
    """Hash password using SHA256 -> bcrypt + salting for storage"""
    return bcrypt.hashpw(hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

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
        
#Function checks if the user exists by searching for their username. If found, it compares the password hash with the stored hash. If both match, the login is successful.
def login_user(ssl_client_socket, data):
    """Handles login logic, sets online flag, and returns username on success"""
    try:
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": "Username and password are required."
            }))
            return None

        users = load_users()["users"]
        user = next((u for u in users if u["username"] == username), None)

        if not user:
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": "Invalid username or password."
            }))
            return None

        # Compare server-side hashed password
        try:
            if not bcrypt.checkpw(hashlib.sha256(password.encode("utf-8")).hexdigest().encode("utf-8"), user["password"].encode("utf-8")):
                send_message(ssl_client_socket, json.dumps({
                    "status": "ERROR",
                    "message": "Invalid username or password."
                }))
                return None
        except Exception as e:
            print(e)

        # Set user as online
        user["online"] = True
        save_users({"users": users})  # Save updated user list

        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": "Login successful."
        }))

        return user["username"]  # Return username for handler to set client_username

    except Exception as e:
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": f"Login failed: {str(e)}"
        }))
        return None

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

def get_user_key(ssl_client_socket, client_username, data):
    friendlist = []
    recipient_found = 0
    friends = False
    print(f"Received request for public key")
    recipient = data["username"]
    userdata = load_users()
    print(f"username to find: '{recipient}'\n looking in {DATA_FILE}")

    # Check if recipient and the requesting are friends
    for user_data in userdata["users"]:
        if user_data["username"] == recipient:
            friendlist = user_data["friends"]
            recipient_found = 1
            print(f"Found recipient {recipient}. Friends list: {friendlist}")
            break
    if not recipient_found:
        print(f"Not able to find {recipient}")
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": f"Not able to find {recipient}"
        }))
    else:
        if friendlist is None:
         print(f"Recipient {recipient} has no friend list data.")
        elif not friendlist: # Handles the case where friendlist is an empty list []
            print(f"{recipient} has no friends.")
            send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "You are not friends with {recipient}"
        }))
        # Loop 2: Check if client is in obtained friendlist
        for friend_username in friendlist: 
            if friend_username == client_username:
                friends = True
                print(f"Confirmed: {client_username} is in {recipient}'s friend list.") # Debug print
                try:
                    user_list = userdata.get("users")  # Iterate through "users"
                    if isinstance(user_list, list):
                        for user in user_list:
                            if isinstance(user, dict) and user.get("username") == recipient: #find matching user, copy and send public key 
                                public_key = user.get("key")
                                print(f"User key: {public_key}\n\n")
                                send_message(ssl_client_socket, json.dumps({
                                    "status": "OK",
                                    "key": public_key
                                    }))
                                print(f"Key sent to {client_username}")
                except Exception as e:
                    print(f"Error retrieving user key")
                    send_message(ssl_client_socket, json.dumps({
                        "status": "ERROR",
                        "message": "Error retrieving public key"
                    }))
                break # Exit loop once friend is found

# Process and save client uploaded files
def upload_file(ssl_client_socket, data):
    print("upload_file function called")
    base_dir = './Files/'
    os.makedirs(base_dir, exist_ok=1) # Ensure directory is available to store client files
    # Get file name
    filename = data["file"]
    filepath = os.path.join(base_dir, filename)
    if not filename or not isinstance(filename, str):
             raise ValueError("Missing or invalid 'file' name in received data.")
    print(f"Attempting to open '{filename}'")
    data = json.dumps(data)
    try:
        with open(filepath, 'w') as f:
            f.write(data)  # Saving the uploaded file to server storage
            send_message(ssl_client_socket, json.dumps({
                "status": "OK",
                "message": "Server successfully uploaded file"
            }))
    except IOError as e:
        print(f"IO Error writing message file {filename}: {e}")
    except Exception as e:
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "ERROR uploading file"
        }))

# Function for user to save a public key to their account
def save_public_key(client_username, user_data):
    key = user_data["key"]
        # 1. Load current data using the robust load function
    all_data = load_users() # load_users already handles locking for read
    # load_users returns {"users": []} on error, check if it's usable
    if not isinstance(all_data.get("users"), list):
            print("Error: Failed to load a valid user data structure.")
            return False

    user_found = False
    # 2. Find the user and update the key 
    for user_record in all_data["users"]:
        if isinstance(user_record, dict) and user_record.get("username") == client_username:
            print(f"Found user '{client_username}'. Updating key.")
            user_record["key"] = key # Update the 'key' field
            user_found = True
            break 

    if not user_found:
        print(f"Error: User '{client_username}' not found in data file.")
        return False

    # 3. Write the data back to the file
    try:
        with open(DATA_FILE, "w", encoding='utf-8') as jsonfileW:
            json.dump(all_data, jsonfileW, indent=4) 
        print(f"Successfully updated public key for '{client_username}' in {DATA_FILE}")
        return True
    except IOError as e:
        print(f"ERROR saving updated record to {DATA_FILE}: {e}")
        return False 
    except Exception as e: 
        print(f"An unexpected error occurred saving the updated record: {e}")

def logout_user(ssl_client_socket, data, client_username=None):
    try:
        set_online(client_username, False)

        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": "Logout successful."
        }))

        return None  # Clear out client_username from session

    except Exception as e:
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": f"Logout failed: {str(e)}"
        }))
        return client_username # Keep user logged in

def set_online(username, status):
    users = load_users()["users"]
    user = next((u for u in users if u["username"] == username), None)

    # Set user as online
    user["online"] = status
    save_users({"users": users})  # Save updated user list

def get_and_send_file(ssl_client_socket, client_username):
    folder_path = './Files/'
    matching_files = ''
    print(client_username)
    # --- 1. Validate Folder Path ---
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found or is not a directory: {folder_path}")
        return matching_files # Return empty list
    try:
        # Iterate through folder, check if json, then find match to username
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path) and filename.lower().endswith('.json'):
                print(f"  Checking file: {filename}") 
                try:
                    with open(file_path, 'r', encoding='utf-8') as f: # Use 'with' for auto-close
                        data = json.load(f)
                        if isinstance(data, dict):
                            # Check if the 'recipient' key exists
                            if "recipient" in data:
                                file_recipient = data["recipient"]
                                if file_recipient == client_username:
                                        match = True
                                if match:
                                    print(f"--> Match found!")
                                    matching_files = (file_path) 
                                    break

                # Handle potential errors during file reading/parsing
                except json.JSONDecodeError:
                    print(f"    Warning: Could not decode JSON from file: {filename}")
                except IOError as e:
                    print(f"    Warning: Could not read file: {filename} - {e}")
                except Exception as e: # Catch any other unexpected errors for this file
                    print(f"    Warning: An unexpected error occurred processing file {filename}: {e}")

    except OSError as e:
        # Handle potential errors listing the directory (e.g., permissions)
        print(f"Error: Could not access directory contents: {folder_path} - {e}")
        return [] # Return empty list
    try:
        with open(file_path, 'r') as encrypted_file:
            file_data = json.load(encrypted_file)
            print(f"Successfully loaded file: {filename}")
    except Exception as e:
        print(f"There was an error retrieving the file: {e}")
    send_message(ssl_client_socket, json.dumps({
        "status" : "OK",
        "message" : file_data
    }))
