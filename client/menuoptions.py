import datetime
import json
import time
import os

from Crypto.Hash import SHA256
from cconnector import send_message, receive_message
from keylogic import generate_key_pair

# Send registration request to the server
def send_registration_request(tls_socket):

    if os.path.isfile("./keys/public.pem"):
        os.remove("./keys/public.pem")
        if os.path.isfile("./keys/private.pem"):
            os.remove("./keys/private.pem")
        
        # Generate new pseudorandom password protected private RSA key and public RSA key
    if not generate_key_pair(SHA256.new(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f").encode()).hexdigest()[:16]):
        print("Key generation failed.")
        return
    public_key = './keys/public.pem'
    try:
        with open(public_key, 'r+') as key_file:
            key_data = key_file.read()
    except Exception as e:
        print(f"Error opening public key file: '{e}'")

    """Send the registration request with user data to the server"""
    registration_data = {
        "action": "register",  # Action type
        "name": input("Enter your full name: "),
        "email": input("Enter your email address: "),
        "username": input("Choose a username: "),
        "password": input("Choose a password (NOTE: must only contain alphanumberic characters and be 16 characters or longer): "),
        "key": key_data
        
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
            # Save account details, send server public key
            try:    
                with open("./client/client_account.json", 'w+') as jsonfile:
                    json.dump(registration_data, jsonfile, indent=3)
            except Exception as e:
                print(f"Error writing client account data")
            # Return to client menu
            input("Returning to menu, press Enter to continue...")

            os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
    except Exception as e:
        print(f"Error sending registration data: {e}")

# Send login request to the server || WIP: CURRENTLY SENDS/RECIEVES NOTIFICATION THAT LOGIN IS NOT YET IMPLEMENTED
def send_login_request(tls_socket):
    login_data = {
        "action": "login"  # Action type
        #"username": input("Enter your username: "),
        #"password": input("Enter your password: ")
    }

    try:
        message = json.dumps(login_data)  # Convert the data into JSON
        send_message(tls_socket, message)  # Send the login request to the server
        print(f"Sent login request")
        response = receive_message(tls_socket, None)  # Wait for the server to respond
        print(f"Login response: {response}")
        # Return to client menu
        input("Returning to menu, press Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
        send_public_key(tls_socket)
    except Exception as e:
        print(f"Error sending login data: {e}")

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
        # Return to main to terminate program
        print(data["key"])
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
    