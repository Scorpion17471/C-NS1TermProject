import socket
import ssl
import logging
import threading

import json

from server_utils import set_online, register_user, login_user, add_user_friend, remove_user_friend, show_online_friends, get_user_key, save_public_key, upload_file, logout_user, get_and_send_file

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
    # 6. Send File -NEEDS LOGIN
    # 7. Logout/Exit

    # Client Instance Main Loop
    try:
        client_username = None
        suspicious_counter = 0
        while True:
            # Receive message from client
            request = receive_message(ssl_client_socket)
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
                # Login existing user (DONE)
                elif action == "login":
                    client_username = login_user(ssl_client_socket, data)
                    data = None # Clear data after processing
                # Add friend (DONE)
                elif action == "add_friend":
                    add_user_friend(ssl_client_socket, data, client_username)  # Call the add_friend function from server_utils.py
                    
                    result = add_user_friend(ssl_client_socket, data, client_username)
                    if result == {"suspicious": 1}:
                        suspicious_counter += 1
                    if suspicious_counter >= 3:
                        send_message(ssl_client_socket, json.dumps({
                            "status": "ERROR",
                            "message": "Too many suspicious actions. Connection will be closed."
                        }))
                        break

                    data = None  # Clear data after processing

                # Remove friend (DONE)
                elif action == "remove_friend":
                    remove_user_friend(ssl_client_socket, data, client_username)
                    
                    result = remove_user_friend(ssl_client_socket, data, client_username)
                    if result == {"suspicious": 1}:
                        suspicious_counter += 1
                    if suspicious_counter >= 3:
                        send_message(ssl_client_socket, json.dumps({
                            "status": "ERROR",
                            "message": "Too many suspicious actions. Connection will be closed."
                        }))
                        break

                    data = None  # Clear data after processing
                    
                # Show online friends (DONE)
                elif action == "show_online":
                    show_online_friends(ssl_client_socket, data, client_username)  # Call the show_online function from server_utils.py
                    
                    result = show_online_friends(ssl_client_socket, data, client_username)
                    if result == {"suspicious": 1}:
                        suspicious_counter += 1
                    if suspicious_counter >= 3:
                        send_message(ssl_client_socket, json.dumps({
                            "status": "ERROR",
                            "message": "Too many suspicious actions. Connection will be closed."
                        }))
                        break                    
                    
                    data = None  # Clear data after processing
                    
                # Send file (DONE)
                elif action == "send_file":
                    upload_file(ssl_client_socket, data, client_username)  # Call the send_file function from
                    
                    result = upload_file(ssl_client_socket, data, client_username)
                    if result == {"suspicious": 1}:
                        suspicious_counter += 1
                    if suspicious_counter >= 3:
                        send_message(ssl_client_socket, json.dumps({
                            "status": "ERROR",
                            "message": "Too many suspicious actions. Connection will be closed."
                        }))
                        break                    
                    data = None  # Clear data after processing

                # Get file (DONE)
                elif action == "download":
                    get_and_send_file(ssl_client_socket,client_username)
                    data = None

                # Logout (DONE)
                elif action == "logout":
                    client_username = logout_user(ssl_client_socket, data, client_username) # Sets client_username to None on successful logout and sends message to user, keeps user logged in and sends message if failed
                    result = logout_user(ssl_client_socket, data, client_username)
                    if result == {"suspicious": 1}:
                        suspicious_counter += 1
                    else:
                        client_username = result
                    if suspicious_counter >= 3:
                        send_message(ssl_client_socket, json.dumps({
                            "status": "ERROR",
                            "message": "Too many suspicious actions. Connection will be closed."
                        }))
                        break

                    data = None
                elif action == "exit":
                    send_message(ssl_client_socket, json.dumps({
                        "status": "OK",
                        "message": "Have a nice day!"
                    }))
                    break
                elif action == "storepk": #Save public key to share with other clients
                    save_public_key(client_username, data)
                elif action == "getpk":
                    get_user_key(ssl_client_socket,client_username, data) 
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
            if client_username:
                set_online(client_username, False)
            ssl_client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        finally:
            ssl_client_socket.close()
            logging.info(f"Closed connection for {client_address}")
            return