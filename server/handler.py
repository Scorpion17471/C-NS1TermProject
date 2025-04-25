import socket
import ssl
import logging
import threading

import json 
from server_utils import register_user, add_user_friend, remove_user_friend, show_online_friends, get_user_key, save_public_key, upload_file, verify_user_credentials, set_user_online
from sconnector import send_message, receive_message

# Program instance main function
def handle_client(ssl_client_socket: ssl.SSLSocket, client_address):
    logging.info(f"Received connection from {client_address}, handling.")

    # Client Instance Main Loop
    # Main functions:
    # 1. Register
    # 2. Login
    # 3. Add Friend -NEEDS LOGIN
    # 4. Remove Friend -NEEDS LOGIN
    # 5. Show Friends Online -NEEDS LOGIN
    # 6. Send DM -NEEDS LOGIN
    # 7. Send File -NEEDS LOGIN
    # 8. Logout/Exit

    # Client Instance Main Loop
    try:
        client_username = None
        while True:
            # Receive message from client
            request = receive_message(ssl_client_socket, None)
            if request is not None:
                try:
                    data = json.loads(request)  # Parse incoming JSON message
                except json.JSONDecodeError:
                    send_message(ssl_client_socket, json.dumps({
                        "status": "ERROR",
                        "message": "Invalid JSON format."
                    }))
                    return

                action = data.get("action")

                # Register new user (DONE)
                if action == "register":
                    register_user(ssl_client_socket, data)  # Call the register_user function from server_utils.py
                    data = None  # Clear data after processing
                # Login existing user ==========================WIP========================== needs to be implemented, set client_username = username on successful login
                elif action == "login":
                    username = data.get("username")
                    password = data.get("password")

                    success, message = verify_user_credentials(username, password)
                    if success:
                        set_user_online(username, True)
                        client_username = username  # Store for session
                        send_message(ssl_client_socket, json.dumps({
                            "status": "OK",
                            "message": "Login successful."
                        }))
                    else:
                        send_message(ssl_client_socket, json.dumps({
                            "status": "ERROR",
                            "message": message
                        }))
                    data = None

                elif action == "add_friend":
                    add_user_friend(ssl_client_socket, data, client_username)  # Call the add_friend function from server_utils.py
                    data = None  # Clear data after processing
                # Remove friend ==========================WIP========================== needs login to verify username
                elif action == "remove_friend":
                    remove_user_friend(ssl_client_socket, data, client_username)
                    data = None  # Clear data after processing
                # Show online friends ==========================WIP========================== needs login to verify username
                elif action == "show_online":
                    show_online_friends(ssl_client_socket, data, client_username)  # Call the show_online function from server_utils.py
                    data = None  # Clear data after processing
                # Send file ==========================WIP========================== needs to be implemented
                elif action == "send_file":
                    #send_file(ssl_client_socket, data, client_username)  # Call the send_file function from
                    data = None  # Clear data after processing
                # Send DM ==========================WIP========================== needs to be implemented
                elif action == "send_dm":
                    #send_dm(ssl_client_socket, data, client_username)  # Call the send_dm function from server_utils.py
                    data = None  # Clear data after processing
                # Logout/Exit ==========================WIP========================== needs to be implemented
                elif action == "logout":
                    send_message(ssl_client_socket, json.dumps({
                        "status": "OK",
                        "message": "Logout functionality not implemented yet."
                    }))
                    #set_offline(client_username)  # Call the set_offline function from server_utils.py
                    client_username = None  # Clear client_username after logout
                    data = None
                elif action == "exit":
                    send_message(ssl_client_socket, json.dumps({
                        "status": "OK",
                        "message": "Have a nice day!"
                    }))
                    break
                elif action == "storepk": #Save public key to share with other clients
                    save_public_key(data)
                elif action == "getpk":
                    get_user_key(ssl_client_socket, data) 
                elif action == "upload":
                    upload_file(ssl_client_socket, data)
                else:
                    send_message(ssl_client_socket, json.dumps({
                        "status": "ERROR",
                        "message": f"Unsupported action: {action}"
                    }))
                    data = None
            request = None
    except socket.error as e:
        print(f"Socket error in handler for {client_address}: {e}")
    finally:
        logging.info(f"Closing handler")
        try:
            ssl_client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        finally:
            ssl_client_socket.close()
            logging.info(f"Closed connection for {client_address}")
            return