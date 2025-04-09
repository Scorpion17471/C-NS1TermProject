import socket
import ssl
import logging
from sconnector import send_message, receive_message

# Program instance main function
def handle_client(tls_client_socket: ssl.SSLSocket, client_address):
    logging.info(f"Received connection from {client_address}, handling.")

    # Client Instance Main Loop
    # Main functions:
    # 1. Register
    # 2. Login
    # 3. Add Friend
    # 4. Send Message
    # 5. Send File
    # 6. Logout

    # Demo client/server exchange
    try:
        output = receive_message(tls_client_socket)
        if output is not None:
            logging.info(f"Received {output} from {client_address}")
            print(f"Received {output} from {client_address}")
            message = "Hello, your message was received"
            send_message(tls_client_socket, message)
    except socket.error as e:
        logging.error(f"Socket error in handler for {client_address}: {e}")
    finally:
        logging.info(f"Closing handler")
        try:
            tls_client_socket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        finally:
            return