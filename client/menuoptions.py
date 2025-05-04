import datetime
import json
import time
import os

from Crypto.Hash import SHA256
from cconnector import send_message, receive_message
from keylogic import generate_key_pair, get_publics
from encrypt import encrypt_file, decrypt_file

# Display initial options to the user
def menu1():
    option = 0
    while option not in [1, 2, 3]:
        try:
            option = int(input("""Welcome to SFTP v1.0! Please register if this is your first time connecting, or login if you already have an account:
                1. Register
                2. Login
                3. Exit
            """))
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 3.")
    return option

# Display session menu options to the user
def menu2():
    option = 0
    while option not in [1, 2, 3, 4, 5, 6]:
        try:
            option = int(input("""Welcome to SFTP v1.0! Please register if this is your first time connecting, or login if you already have an account:
                1. Add Friend
                2. Remove Friend
                3. Show Friends Online
                4. Send File
                5. Download File
                6. Logout
            """))
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 6.")
    return option

# Send registration request to the server
def send_registration_request(tls_socket):
    registration_data = {
        "action": "register",  # Action type
        "name": input("Enter your full name: "),
        "email": input("Enter your email address: "),
        "username": input("Choose a username: "),
        "password": input("Choose a password (NOTE: must only contain alphanumberic characters and be 16 characters or longer): "),
        "key":  get_publics()  # Get the public key as string from the file
    }

    try:
        message = json.dumps(registration_data)  # Convert the data into JSON
        send_message(tls_socket, message)  # Send the registration request to the server
        response = receive_message(tls_socket, None)  # Wait for the server to respond
        if response is not None:
            try:
                data = json.loads(response)  # Parse incoming JSON message
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return
            # Print server response
            if data["status"] == "ERROR":
                print(f"\nRegistration failed: {data['message']}")
            elif data["status"] == "OK":
                print(f"\n{data['message']}")
    except Exception as e:
        print(f"Error sending registration data: {e}")

# Send login request to the server || WIP: CURRENTLY SENDS/RECIEVES NOTIFICATION THAT LOGIN IS NOT YET IMPLEMENTED | RETURN TRUE IF LOGIN SUCCESSFUL, FALSE IF FAILED
def send_login_request(tls_socket):
    login_data = {
        "action": "login",
        "username": input("Enter your username: "),
        "password": input("Enter your password: ")
    }

    try:
        message = json.dumps(login_data)
        send_message(tls_socket, message)
        response = receive_message(tls_socket, None)

        if response is not None:
            try:
                data = json.loads(response)
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return False

            if data["status"] == "OK":
                print(f"\n{data['message']}")
                send_public_key(tls_socket)
                return True
            elif data["status"] == "ERROR":
                print(f"\nLogin failed: {data['message']}")
                return False
    except Exception as e:
        print(f"Error sending login data: {e}")
        return False

# Send exit request to the server
def send_exit_request(tls_socket):
    exit_data = {
        "action": "exit"  # Action type
    }
    try:
        message = json.dumps(exit_data)  # Convert the data into JSON
        send_message(tls_socket, message)  # Send the exit request to the server
        response = receive_message(tls_socket, None)  # Wait for the server to respond
        try:
            data = json.loads(response)  # Parse incoming JSON message
        except json.JSONDecodeError:
            print("Invalid JSON format in response, please try again.")
            return
        send_public_key(tls_socket)
    except Exception as e:
        print(f"Error sending exit data: {e}")

def send_public_key(tls_socket): # Get the public key as string from the file
    data = {
        "action": "storepk",
        "key": get_publics()
    }
    message = json.dumps(data)
    try:
        send_message(tls_socket, message)
    except Exception as e:
        print(f"Error sending public key: {e}")
    

# Send add friend request to the server
def add_friend(tls_socket_client):
    friend_data = {
        "action": "add_friend",  # Action type
        "friend_username": input("Enter the username of the friend you want to add: ")
    }

    try:
        message = json.dumps(friend_data)  # Convert the data into JSON
        send_message(tls_socket_client, message)  # Send the add friend request to the server
        response = receive_message(tls_socket_client, None)  # Wait for the server to respond
        if response is not None:
            try:
                data = json.loads(response)  # Parse incoming JSON message
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return
            # Print server response
            if data["status"] == "ERROR":
                print(f"\nFailed to add friend: {data['message']}")
            elif data["status"] == "OK":
                print(f"\n{data['message']}")
    except Exception as e:
        print(f"Error sending add friend data: {e}")

# Send remove friend request to the server
def remove_friend(tls_socket_client):
    friend_data = {
        "action": "remove_friend",  # Action type
        "friend_username": input("Enter the username of the friend you want to remove: ")
    }

    try:
        message = json.dumps(friend_data)  # Convert the data into JSON
        send_message(tls_socket_client, message)  # Send the remove friend request to the server
        response = receive_message(tls_socket_client, None)  # Wait for the server to respond
        if response is not None:
            try:
                data = json.loads(response)  # Parse incoming JSON message
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return
            # Print server response
            if data["status"] == "ERROR":
                print(f"\nFailed to remove friend: {data['message']}")
            elif data["status"] == "OK":
                print(f"\n{data['message']}")
    except Exception as e:
        print(f"Error sending remove friend data: {e}")

# Get online friends
def show_online(tls_socket_client):
    list_request = {
        "action": "show_online"
    }
    try:
        message = json.dumps(list_request)  # Convert the data into JSON
        send_message(tls_socket_client, message)  # Send the remove friend request to the server
        response = receive_message(tls_socket_client, None)  # Wait for the server to respond
        if response is not None:
            try:
                data = json.loads(response)  # Parse incoming JSON message
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return
            # Print server response
            if data["status"] == "ERROR":
                print(f"\nFailed to get friend list: {data['message']}")
            elif data["status"] == "OK":
                print(f"Friends Online:\n\n\t{data['message']}\n")
    except Exception as e:
        print(f"Error sending request for online friends data: {e}")

def send_file(tls_socket_client):

    # Prompt user for file to upload
    file_path = input("Enter the absolute path of the file you want to send: ")
    file_name = file_path.split('\\' if os.name == 'nt' else '/')[-1]
    
    if not file_path:
        print("Error: No filename provided.")
        return

    if not os.path.exists(file_path):
        print(f"Error: File not found at '{file_path}'")
        return

    print(f"Reading file: {file_name}...")
    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    if not file_bytes:
        print(f"Warning: File '{file_name}' is empty.")

    payload = encrypt_file(tls_socket_client, file_bytes, file_name)
    if not payload:
        print(f"Error encrypting file")
        return
    message = json.dumps(payload)
    try:
        print("sending encrypted file...")
        send_message(tls_socket_client, message)
        response = receive_message(tls_socket_client, None)
        if response is not None:
            try:
                data = json.loads(response)  # Parse incoming JSON message
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return
            # Print server response
            if data["status"] == "ERROR":
                print(f"\nSend failed: {data['message']}")
            elif data["status"] == "OK":
                print(f"\n{data['message']}")
                # Save account details, send server public key
        else:
            print(f"Response {response}")
            return
    except Exception as e:
         print("Error in client/encrypt.py")

def download_file(tls_socket_client):
    # Send server check check message
    # Server verifies
    # User selects file (if multiple) & downloads
    senddata = {
        "action": "download"
    }
    message = json.dumps(senddata)
    try:
        send_message(tls_socket_client, message)
        response = receive_message(tls_socket_client, None)
        payload = json.loads(response)
        if payload["status"] == "ERROR":
            print("Server experienced issues retrieving data")
    except Exception as e:
        print(f"Error sending/receiving message: {e}")

    decrypted_data = decrypt_file(tls_socket_client, payload["message"])
    filename = payload["message"]["file"]
    save_file = os.path.join(os.getcwd(), "downloads", filename)
    try:
        with open(save_file, "wb") as f:
            f.write(decrypted_data)
        print("File saved")
    except KeyError as e:
        print(f"ERROR: Missing expected key in received payload: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during decryption: {e}")


def send_logout_request(tls_socket_client):
    list_request = {
        "action": "logout"
    }
    try:
        message = json.dumps(list_request)  # Convert the data into JSON
        send_message(tls_socket_client, message)  # Send the remove friend request to the server
        response = receive_message(tls_socket_client, None)  # Wait for the server to respond
        if response is not None:
            try:
                data = json.loads(response)  # Parse incoming JSON message
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return
            # Print server response
            if data["status"] == "ERROR":
                print(f"\nFailed to logout: {data['message']}")
                return True # User is still logged in
            elif data["status"] == "OK":
                print(f"You have been logged out\n")
                return False # User is logged out
    except Exception as e:
        print(f"Error sending logout request: {e}")
        return True # User is still logged in