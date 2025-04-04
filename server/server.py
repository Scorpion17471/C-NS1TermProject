import socket
import ssl

# Server function to attempt to push data to the corresponding client
# returns True if entire payload was successfully sent
# returns False if failed 3 times
def server_send(tls_client_socket, payload):
    for i in range(3):
        try:
            # Send the payload with delimiters
            # Begin Message = "\/\/" written as "\\/\\/"
            # End Message = "/\/\" written as "/\\/\\"
            tls_client_socket.sendall(("\\/\\/" + payload + "/\\/\\").encode('utf-8'))
            i = 10
        except socket.error as e:
            print(f"Error sending payload: {e}")
            continue
    if i == 10:
        return True
    else:
        return False

# Server function to receive data from the client
# returns payload if it was received
# returns None if failed to receive data
def server_receive(tls_client_socket):
    tls_client_socket.settimeout(5)  # Set a timeout for receiving data
    try:
        output = ""
        response = tls_client_socket.recv(1024).decode('utf-8')
        output += response
        while output[-4:] != "/\\/\\":
            response = tls_client_socket.recv(1024).decode('utf-8')
            output += response
        output = output[4:-4]  # Remove the delimiters from the end of the output
    except socket.error as e:
        output = None
        print(f"Error receiving response: {e}")
    finally:
        tls_client_socket.settimeout(None) # Reset timeout after receiving data or erroring out
        return output

def main():
    # Server configuration
    HOST = '127.0.0.1'  # Localhost
    PORT = 8443         # Port to listen on
    CERT_FILE = './cert.pem'  # Path to server certificate
    KEY_FILE = './serverr.pem'   # Path to server private key

    # Create SSL context to wrap socket in TLS wrapper
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)  # Load the server certificate and key

    #################################################################################

    context.check_hostname = False  # Disable hostname checking for testing purposes
    context.verify_mode = ssl.CERT_NONE  # Disable certificate verification for testing purposes

    #################################################################################

    # Create socket, bind to address, set for listening

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server listening on {HOST}:{PORT} without TLS")
        while True:
            try:
                # Accept client connections
                client_socket, client_address = server_socket.accept()
                print(f"Connection established with {client_address}")
                # Wrap the socket with TLS/SSL context
                tls_client_socket = context.wrap_socket(client_socket, server_side=True)
                print(f"TLS Connection established with {client_address} using TLS version: {tls_client_socket.version()}")
                # Demo Server Recieve client communication
                output = server_receive(tls_client_socket)
                if output is not None:
                    print(f"Received: {output}")
                # Demo Server Send message to client
                message = "Hello, TLS Client!"
                server_send(tls_client_socket, message)

                # Server Actions:
                    # Server Requests: Send a message to the client
                        # use server_send function to send data to the client
                        #
                        # server_send(tls_client_socket, {message payload})

                    # Client Responses: Receive a response from the server
                        # use client_receive function to receive data from the server
                        #
                        # client_receive(tls_socket_client)
            except Exception as e:
                print(f"Error during communication: {e}")
            finally:
                tls_client_socket.close()
    except Exception as e:
        print("\nServer shutting down due to error.")
    finally:
        print("Server socket closed.")
        server_socket.close()

if __name__ == "__main__":
    main()