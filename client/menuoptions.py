import datetime
import json
import time
import os

from Crypto.Hash import SHA256
from cconnector import send_message, receive_message
from keylogic import generate_key_pair, get_publics

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
                print(f"\nRegistration failed: {data["message"]}")
            elif data["status"] == "OK":
                print(f"\n{data["message"]}")
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
    except Exception as e:
        print(f"Error sending exit data: {e}")

def send_public_key(tls_socket):
    try:
        with open('./client_account.json', 'r+') as jsonfile:
            data = json.load(jsonfile)
            if isinstance(data, dict) and 'name' in data:
                name = data["name"]
                print(name)
    except Exception as e:
        print(f"Error opening gathering account information: '{e}'")
    public_key = './keys/public.pem'
    try:
        with open(public_key, 'r+') as key_file:
            key_data = key_file.read()
    except Exception as e:
        print(f"Error opening public key file: '{e}'")
    print(f"Public key: '{key_data}")
    data = {
        "action": "storepk",
        "name": name, 
        "key": key_data
    }
    message = json.dumps(data)
    try:
        send_message(tls_socket, message)
    except Exception as e:
        print(f"Error sending public key: {e}")
    
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
                5. Send DM
                6. Logout
            """))
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 6.")
    return option

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
                print(f"\nFailed to add friend: {data["message"]}")
            elif data["status"] == "OK":
                print(f"\n{data["message"]}")
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
                print(f"\nFailed to remove friend: {data["message"]}")
            elif data["status"] == "OK":
                print(f"\n{data["message"]}")
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
                print(f"\nFailed to get friend list: {data["message"]}")
            elif data["status"] == "OK":
                print(f"Friends Online:\n\n\t{data["message"]}\n")
    except Exception as e:
        print(f"Error sending request for online friends data: {e}")

#send_file(tls_socket_client)
#send_DM(tls_socket_client)