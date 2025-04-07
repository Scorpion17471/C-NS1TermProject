import socket
import logging
from common.protocol import send_message, receive_message

def handle_client(tls_client_socket: socket.socket, client_address):
    logging.info(f"Received connection from {client_address}, handling.")
    try:
        output = receive_message(tls_client_socket)
        if output is not None:
            logging.info(f"Received {output} from {client_address}")
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
            tls_client_socket.close() 
