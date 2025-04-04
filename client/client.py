import socket
import ssl

# Client function to attempt to push data to the server
# returns True if entire payload was successfully sent
# returns False if failed 3 times
def client_send(tls_socket_client, payload):
    for i in range(3):
        try:
            # Send the payload with delimiters
            # Begin Message = "\/\/" written as "\\/\\/"
            # End Message = "/\/\" written as "/\\/\\"
            tls_socket_client.sendall(("\\/\\/" + payload + "/\\/\\").encode('utf-8'))
            i = 10
        except socket.error as e:
            print(f"Error sending payload: {e}")
            continue
    if i == 10:
        return True
    else:
        return False

# Client function to receive data from the server
# returns payload if it was received
# returns None if failed to receive data
def client_receive(tls_socket_client):
    tls_socket_client.settimeout(5)  # Set a timeout for receiving data
    try:
        output = ""
        response = tls_socket_client.recv(1024).decode('utf-8')
        output += response
        while output[-4:] != "/\\/\\":
            response = tls_socket_client.recv(1024).decode('utf-8')
            output += response
        output = output[4:-4]  # Remove the delimiters from the end of the output
    except socket.error as e:
        output = None
        print(f"Error receiving response: {e}")
    finally:
        tls_socket_client.settimeout(None) # Reset timeout after receiving data or erroring out
        return output

def main():
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
            # Demo Client Send message to server
            message = "Hello, TLS Server!"
            client_send(tls_socket_client, message)
            # Demo Client Recieve response from server
            response = client_receive(tls_socket_client)
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

        except socket.error as e:
            print(f"Could not connect to server due to error: {e}")
            return
        finally:
            print("Closing connection.")
            tls_socket_client.close()

if __name__ == "__main__":
    main()