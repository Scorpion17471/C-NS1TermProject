import socket
import ssl

# Server configuration
HOST = '127.0.0.1'  # Localhost
PORT = 8443         # Port to listen on
CERT_FILE = 'server.crt'  # Path to server certificate
KEY_FILE = 'server.key'   # Path to server private key

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create SSL context to wrap socket in TLS wrapper
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.check_hostname = False  # Disable hostname checking for testing purposes
context.verify_mode = ssl.CERT_NONE  # Disable certificate verification for testing purposes
#context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE) # Load the server certificate and key

# Bind and listen
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT} with TLS")

# Wrap the socket with TLS/SSL context
tls_server_socket = context.wrap_socket(server_socket, server_side=True)

while True:
    try:
        # Accept client connections
        client_socket, client_address = tls_server_socket.accept()
        print(f"Connection established with {client_address}")

        # Handle client communication
        try:
            data = client_socket.recv(1024).decode('utf-8')
            print(f"Received: {data}")
            client_socket.sendall(b"Hello, TLS Client!")
        except Exception as e:
            print(f"Error during communication: {e}")
        finally:
            client_socket.close()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        tls_server_socket.close()