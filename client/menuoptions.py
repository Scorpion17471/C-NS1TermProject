import json
import time
import os

from cconnector import send_message, receive_message

# Send registration request to the server
def send_registration_request(tls_socket):
    """Send the registration request with user data to the server"""
    registration_data = {
        "action": "register",  # Action type
        "name": input("Enter your full name: "),
        "email": input("Enter your email address: "),
        "username": input("Choose a username: "),
        "password": input("Choose a password (NOTE: must only contain alphanumberic characters and be 16 characters or longer): ")
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
        print(data["message"])
    except Exception as e:
        print(f"Error sending exit data: {e}")