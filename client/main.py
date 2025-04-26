import socket
import ssl
import datetime
import os
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

from keylogic import generate_key_pair, get_private, get_public
from menuoptions import menu1, menu2, send_registration_request, send_login_request, send_exit_request, add_friend, remove_friend, show_online, send_logout_request#, send_DM
#from encrypt import send_file
import json

def main():
    # Check if client key directory exists/make if not
    if not os.path.isdir("./keys"):
        os.makedirs("./keys")
    # Check if both client keys can be retrieved, if not generate new keys and remove old keys if they exist
    if not get_public() or not get_private():
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
            login = False
            while True:
                input("Press Enter to continue to menu")
                os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
                option = 0
                # Session menu
                if login:
                    option = menu2()
                    # Add friend
                    if option == 1:
                        add_friend(tls_socket_client)

                    # Remove friend
                    elif option == 2:
                        remove_friend(tls_socket_client)
                    
                    # Show online friends
                    elif option == 3:
                        show_online(tls_socket_client)

                    # Send file ===============WIP===============
                    #elif option == 4:
                        #send_file(tls_socket_client)

                    # Send DM ===============WIP===============
                    #elif option == 5:
                        #send_message(tls_socket_client)
                    
                    # Logout ===============WIP===============
                    elif option == 6:
                        login = send_logout_request(tls_socket_client)
                # Registration/login menu
                else:
                    option = menu1()
                    # Register new user
                    if option == 1:
                        send_registration_request(tls_socket_client)

                    # Login existing user ===============WIP===============
                    elif option == 2:
                        login = send_login_request(tls_socket_client)

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