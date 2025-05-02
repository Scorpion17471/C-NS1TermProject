import json
import os
import hashlib
import random
import bcrypt

from Crypto.Hash import SHA256

from sconnector import send_message, receive_message
from server_utils import randomwait, hash_password, load_users, save_users, user_exists, get_friends, set_online

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
    # Check if password is at least 16 characters long and contains only letters and/or numbers
    elif (len(data["password"]) < 16) or (not data["password"].isalnum()):
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "Password must be at least 16 characters long and contain only both letters and numbers."
        }))
    # If all validation checks pass, call create_user function
    else:
        if user_exists(data["username"]):
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": "Username is already taken."
            }))
            return
        user = {
            "name": data["name"],
            "email": data["email"],
            "username": data["username"],
            "password": hash_password(data["password"]),
            "online": False,
            "friends": [],
            "key": data["key"]
        }
        userdata = load_users()
        userdata["users"].append(user)
        try:
            save_users(userdata)  # Save new user to JSON file
            send_message(ssl_client_socket, json.dumps({
                "status": "OK",
                "message": "Registration successful"
            }))
        except Exception as e:
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": f"Failed to create user account: {str(e)}"
            }))

#Function checks if the user exists by searching for their username. If found, it compares the password hash with the stored hash. If both match, the login is successful.
def login_user(ssl_client_socket, data):
    """Handles login logic, sets online flag, and returns username on success"""
    try:
        username = data.get("username")
        password = data.get("password")

        if not (username or password):
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
def add_user_friend(ssl_client_socket, data, client_username=None):
    # If user is not logged in, wait for 0.1 to 1.3 seconds before sending false OK message
    if not client_username:
        randomwait()
        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": f"{data["friend_username"]} added to friends list if registered and not in list already"
        }))
        return {"suspicious": 1}
    elif client_username == data["friend_username"]:
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": f"Cannot add self to friends list"
        }))
        return {"suspicious": 0}
    else:
        userdata = load_users()
        user = next((u for u in userdata["users"] if u["username"] == client_username), None)
        if user and user_exists(data["friend_username"]):
            if not (data["friend_username"] in user["friends"]):
                user["friends"].append(data["friend_username"])
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
        finally:
            return {"suspicious": 0}

# Function to handle adding friends
def remove_user_friend(ssl_client_socket, data, client_username=None):
    # If user is not logged in, wait for 0.7 to 1.9 seconds before sending false OK message
    if not client_username:
        randomwait(7, 19)
        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": f"{data['friend_username']} removed from friends list/was not in friends list"
        }))
        return {"suspicious": 1}
    else:
        userdata = load_users()
        # Remove friend from user's friend list if they exist, do nothing if not
        user = next((u for u in userdata["users"] if u["username"] == client_username), None)
        if user:
            if data["friend_username"] in user["friends"]:
                user["friends"].remove(data["friend_username"])
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
        finally:
            return {"suspicious": 0}

# Function to show online friends
def show_online_friends(ssl_client_socket, data, client_username=None):
    # If user is not logged in, wait for 0.4 to 2.6 seconds before sending false OK message
    if not client_username:
        randomwait(4, 26)
        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": f"No Friends Online"
        }))
        return {"suspicious": 1}
    else:
        try:
            # Get online users
            friends = get_friends(load_users(), client_username)
            # If no friends online, notify, else return list of friends
            if not friends:
                send_message(ssl_client_socket, json.dumps({
                    "status": "OK",
                    "message": f"No Friends Online"
                }))
            else:
                send_message(ssl_client_socket, json.dumps({
                    "status": "OK",
                    "message": "\n\t".join(friends)
                }))
        except Exception as e:
            send_message(ssl_client_socket, json.dumps({
                "status": "ERROR",
                "message": f"Failed to get online friends: {str(e)}"
            }))
        finally:
            return {"suspicious": 0}

# Process and save client uploaded files
def upload_file(ssl_client_socket, data, client_username=None):
    # If user is not logged in, wait for 0.6 to 3.8 seconds before sending false ERROR message
    if not client_username:
        randomwait(6, 38)
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "ERROR uploading file"
        }))
        return {"suspicious": 1}
    print("upload_file function called")
    base_dir = './files/'
    os.makedirs(base_dir, exist_ok=1) # Ensure directory is available to store client files
    # Get file name
    file = data["file"]
    file_name = file+".json"
    print(f"File name {file_name}")
    filepath = os.path.join(base_dir, file_name)
    if not (file or isinstance(file, str)):
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
    finally:
        return {"suspicious": 0}

def get_and_send_file(ssl_client_socket, client_username=None):
    # If user is not logged in, wait for 0.9 to 4.3 seconds before sending false ERROR message
    if not client_username:
        randomwait(9, 43)
        send_message(ssl_client_socket, json.dumps({
            "status": "ERROR",
            "message": "ERROR retrieving files"
        }))
        return {"suspicious": 1}
    folder_path = './files/'
    matching_files = ''
    print(client_username)
    # --- 1. Validate Folder Path ---
    if not os.path.isdir(folder_path):
        print(f"Error: Folder not found or is not a directory: {folder_path}")
        return {"suspicious": 0}
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
        return {"suspicious": 0}
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
    finally:
        return {"suspicious": 0}

def logout_user(ssl_client_socket, data, client_username=None):
    # If user is not logged in, wait for 0.9 to 4.3 seconds before sending false ERROR message
    if not client_username:
        send_message(ssl_client_socket, json.dumps({
            "status": "OK",
            "message": "Logout successful."
        }))
        return None
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
            "message": "Logout failed."
        }))
        return client_username # Keep user logged in