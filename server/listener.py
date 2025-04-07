import socket
import ssl
import sys, os, logging

try:
    from server.handler import handle_client
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from handler import handle_client
    except ImportError:
        print("Error: Cannot import handle_client from server.handler or handler.")

def start_listener(host: str, port: int, cert_file: str, key_file: str):
    # Sets up sockets to listen and accept, wrap TLS and use call the handler
    # 4 Main Functions: 1. Set up SSL context 2. Set up socket  3. Main loop accepts connections 4. Ends connections and close sockets
    # Start w/ loading cert

    # Set SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Load Certs
    try:
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        logging.info(f"SSL Cert loaded successfully")
    except Exception as e:                                           
        logging.error(f"Fatal error loading cert key: {e}")
        return
    
    # Set up socket server
    server_socket=None
    try:
        #TCP Socket using IPv4
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f" Server listening on {host}:{port} ")
    except Exception as e:
        logging.error(f"Fatal error setting up socket: {e}")
        if server_socket:
            server_socket.close()
        return
    # Main loop
    try:
        while True:
            client_socket = None
           #tls_client_socket = None        Will be used when TLS is set up
            client_address = None
            try:
                #Accept connection to client
                client_socket, client_address = server_socket.accept()
                print(f"Accepted connection from: {client_address}")
                #TLS Wrap the connection
                tls_client_socket = context.wrap_socket(client_socket, server_side=True)
                #Pass off to handler
                handle_client(tls_client_socket, client_address)
            # except ssl.SSLError as e:
            #     print(f"SSL ERROR during handshake with {client_address}: {e}")
            #     # Handshake failed, ensure the plain socket is closed if it exists        Exception handling for TLS handshake
            #     if client_socket and not tls_client_socket:
            #         try:
            #             client_socket.close()
            #         except socket.error: pass 
            except Exception as e:
                print(f"ERROR during accept/wrap for {client_address}: {e}")
                # if client_socket and not tls_client_socket:
                #     try:
                #         client_socket.close()
                #     except socket.error: pass
                continue #Wait for the next connection
    except Exception as e:
        print(F"\nUnexpected server error: {e}")
    #close the socket
    finally:
        if server_socket:
            server_socket.close()