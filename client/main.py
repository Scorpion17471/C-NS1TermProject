import socket
import ssl
import datetime
import os
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from cconnector import send_message, receive_message
from keylogic import generate_key_pair, get_private, get_public

import json

def send_registration_request(tls_socket, name, email, username, password):
    """Send the registration request with user data to the server"""
    registration_data = {
        "action": "register",  # Action type
        "name": name,
        "email": email,
        "username": username,
        "password": password
    }

    try:
        message = json.dumps(registration_data)  # Convert the data into JSON
        send_message(tls_socket, message)  # Send the registration request to the server
        print(f"Sent registration request for {username}")
    except Exception as e:
        print(f"Error sending registration data: {e}")

def main():
    # Check if client key directory exists/make if not
    if not os.path.isdir("./keys"):
        os.makedirs("./keys")
    # Check if both client keys can be retrieved, if not generate new keys and remove old keys if they exist
    if not get_private() or not get_public():
        if os.path.isfile("./keys/public.pem"):
            os.remove("./keys/public.pem")
        if os.path.isfile("./keys/private.pem"):
            os.remove("./keys/private.pem")
        
        # Generate new pseudorandom password protected private RSA key and public RSA key
        if not generate_key_pair(SHA256.new(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f").encode()).hexdigest()[:16]):
            print("Key generation failed.")
            return

    # Server details
    server_address = '127.0.0.1'  # Replace with the server's address
    server_port = 8443           # Replace with the server's port

    # Create a socket and wrap it with SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    
    context.check_hostname = False  # Disable hostname checking for testing purposes
    context.verify_mode = ssl.CERT_NONE  # Disable certificate verification for testing purposes

    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as e:
        # Terminate if socket creation fails
        print(f"Could not create socket due to error: {e}")
        return

    with context.wrap_socket(sock, server_hostname=server_address) as tls_socket_client:
        try:
            # Connect to the server
            tls_socket_client.settimeout(5)  # Set a timeout for the connection
            tls_socket_client.connect((server_address, server_port))
            print(f"Connected to the server using TLS using version {tls_socket_client.version()}.")
            tls_socket_client.settimeout(None) # Reset timeout after connection

            ### MAIN CLIENT LOOP ###

            # Demo Client Send message to server
            message = "Hello, TLS Server!"
            send_message(tls_socket_client, message)

            # Demo Client Recieve response from server
            response = receive_message(tls_socket_client)
            if response is not None:
                print(f"Received: {response}")

            # Client Actions:
                # Client Requests: Send a message to the server
                    # use client_send function to send data to the server
                    #
                    # client_send(tls_socket_client, {message payload})

                # Client Responses: Receive a response from the server
                    # use client_receive function to receive data from the server
                    #
                    # client_receive(tls_socket_client)
                    #
                    # Code below is demo recieve of Server Hello to Client for testing connection to server
                        #################################################################################
                        # response = tls_socket_client.recv(1024).decode('utf-8')
                        # print(f"\\/\\/Received: {response}/\\/\\")
                        #################################################################################
            
            ### MAIN CLIENT LOOP END ###

                    
             # Collect user registration details
            name = input("Enter your full name: ")
            email = input("Enter your email address: ")
            username = input("Choose a username: ")
            password = input("Choose a password: ")

            # Send registration request to the server
            send_registration_request(tls_socket_client, name, email, username, password)

            # Receive the server response after registration request
            response = receive_message(tls_socket_client)
            if response:
                print(f"Server response: {response}")
            else:
                print("No response from server.")        
            
            #################################################################################
            
            ### MAIN CLIENT LOOP END ###

        except socket.error as e:
            print(f"Could not connect to server due to error: {e}")
            return
        finally:
            print("Closing connection.")
            tls_socket_client.close()

if __name__ == "__main__":
    main()