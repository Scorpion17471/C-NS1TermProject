import socket
import ssl
import logging
import threading

import json 
from server_utils import register_user # Using utility function
from sconnector import send_message, receive_message

# Program instance main function
def handle_client(ssl_client_socket: ssl.SSLSocket, client_address):
    logging.info(f"Received connection from {client_address}, handling.")

    # Client Instance Main Loop
    # Main functions:
    # 1. Register
    # 2. Login
    # 3. Add Friend
    # 4. Send Message
    # 5. Send File
    # 6. Logout

    # Client Instance Main Loop
    try:
        while True:
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

                if action == "register":
                    register_user(ssl_client_socket, data)  # Call the register_user function from server_utils.py
                    data = None  # Clear data after processing
                elif action == "login":
                    send_message(ssl_client_socket, json.dumps({
                        "status": "OK",
                        "message": "Login functionality not implemented yet."
                    }))
                    data = None  # Clear data after processing
                elif action == "exit":
                    send_message(ssl_client_socket, json.dumps({
                        "status": "OK",
                        "message": "Have a nice day!"
                    }))
                    break
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