import socket
import logging

# Server function to attempt to push data to the corresponding client
# returns True if entire payload was successfully sent
# returns False if failed 3 times
def send_message(tls_client_socket, payload):
    for i in range(3):
        try:
            # Send the payload with delimiters
            # Begin Message = "\/\/" written as "\\/\\/"
            # End Message = "/\/\" written as "/\\/\\"
            tls_client_socket.sendall(("\\/\\/" + payload + "/\\/\\").encode('utf-8'))
            i = 10
        except socket.error as e:
            logging.warning(f"Error sending payload: {e}")
            continue
    if i == 10:
        return True
    else:
        return False

# Server function to receive data from the client
# returns payload if it was received
# returns None if failed to receive data
def receive_message(tls_client_socket):
    tls_client_socket.settimeout(5)  # Set a timeout for receiving data
    try:
        output = ""
        response = tls_client_socket.recv(1024).decode('utf-8')
        output += response
        while output[-4:] != "/\\/\\":
            response = tls_client_socket.recv(1024).decode('utf-8')
            output += response
        output = output[4:-4]  # Remove the delimiters from the end of the output
    
    except socket.timeout:
        logging.warning(f"Timeout after 5 seconds")
        return None
    except socket.error as e:
        output = None
        logging.error(f"Error receiving response: {e}")
    finally:
        tls_client_socket.settimeout(None) # Reset timeout after receiving data or erroring out
        return output
