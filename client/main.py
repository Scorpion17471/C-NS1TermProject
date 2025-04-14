import socket
import ssl
import datetime
import os
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from keylogic import generate_key_pair, get_private, get_public
from menuoptions import send_registration_request, send_login_request, send_exit_request

import json

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
            while True:
                # Display menu options to the user
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
                
                # Register new user
                if option == 1:
                    send_registration_request(tls_socket_client)

                # Login existing user
                elif option == 2:
                    send_login_request(tls_socket_client)

                # Exit the program
                elif option == 3:
                    send_exit_request(tls_socket_client)
                    break
            ### MAIN CLIENT LOOP END ###
        except KeyboardInterrupt as e:
            try:
                send_exit_request(tls_socket_client)
            finally:
                pass
        except socket.error as e:
            print(f"Could not connect to server due to error: {e}")
            return
        finally:
            print("Closing connection.")
            tls_socket_client.close()
            print("Connection closed.")

if __name__ == "__main__":
    main()