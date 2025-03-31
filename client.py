import socket
import ssl

def main():
    # Server details
    server_address = 'localhost'  # Replace with the server's address
    server_port = 12345           # Replace with the server's port

    # Create a socket and wrap it with SSL
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False  # Disable hostname checking (use with caution)
    context.verify_mode = ssl.CERT_NONE  # Disable certificate verification (use with caution)

    with socket.create_connection((server_address, server_port)) as sock:
        with context.wrap_socket(sock, server_hostname=server_address) as tls_sock:
            print("Connected to the server using TLS.")
            
            # Send a message to the server
            message = "Hello, TLS Server!"
            tls_sock.sendall(message.encode('utf-8'))
            print(f"Sent: {message}")

            # Receive a response from the server
            response = tls_sock.recv(1024).decode('utf-8')
            print(f"Received: {response}")

if __name__ == "__main__":
    main()