import socket
import ssl

def main():
    # Server details
    server_address = '127.0.0.1'  # Replace with the server's address
    server_port = 8443           # Replace with the server's port

    # Create a socket and wrap it with SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # Disable hostname checking for testing purposes
    context.verify_mode = ssl.CERT_NONE  # Disable certificate verification for testing purposes

    with socket.create_connection((server_address, server_port)) as sock:
        with context.wrap_socket(sock, server_hostname=server_address) as tls_socket_client:
            print("Connected to the server using TLS.")
            
            # Send a message to the server
            message = "Hello, TLS Server!"
            tls_socket_client.sendall(message.encode('utf-8'))
            print(f"Sent: {message}")

            # Receive a response from the server
            response = tls_socket_client.recv(1024).decode('utf-8')
            print(f"Received: {response}")

if __name__ == "__main__":
    main()