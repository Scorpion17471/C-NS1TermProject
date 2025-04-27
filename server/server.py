import socket
import ssl
import logging
import concurrent.futures

from handler import handle_client

def run_server(host: str, port: int, cert_file: str, key_file: str):
    # Sets up socket server that takes in connections, wraps them in SSL, then creates a child process to handle the connection.
    # 6 Main Functions:
    #   1. Set up SSL context
    #   2. Set up socket
    #   3. Main loop accepts connections
    #   4. Wrap new connection in SSL
    #   5. Create child process to handle connection
    #   6. Ends connections and close sockets

    # 1. Set SSL context
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    # Load Certs
    try:
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        logging.info(f"SSL Cert loaded successfully")
    except Exception as e:                                           
        logging.error(f"Fatal error loading cert key: {e}")
        return
    


    # 2. Set up socket server
    server_socket=None
    try:
        #TCP Socket using IPv4
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(5)
        logging.info(f" Server listening on {host}:{port} ")
        print(f" Server online and listening on {host}:{port} ")
    except Exception as e:
        logging.error(f"Fatal error setting up socket: {e}")
        if server_socket:
            server_socket.close()
        return
    


    # 3. Server Connection Main loop
    try:
        # Max Client Connections = 16
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            #active_connections = []  # List to keep track of active connections
            while True:
                try:
                    #-----Accept connection to client
                    server_socket.settimeout(5)  # Set a 5s timeout for accepting connections so server doesn't hang forever when KeyboardInterrupt is sent
                    client_socket, client_address = server_socket.accept()
                    print(f"Accepted connection from: {client_address}")
                    logging.info(f"Accepted connection from: {client_address}")

                    # 4. Try to wrap socket with SSL
                    try:
                        ssl_client_socket = context.wrap_socket(client_socket, server_side=True)



                        # 5. Create a child process to handle the connection WIP
                        executor.submit(handle_client, ssl_client_socket, client_address)
                        logging.info(f"New thread created to handle {client_address[0]}: {str(client_address[1])}.")
                        ssl_client_socket = 1



    # 6. End connections and close sockets

                    # wrap_socket may throw SSLError 
                    except ssl.SSLError as wrap_err:
                        logging.error(f"Error during SSL wrap for {client_address}: {wrap_err}")
                        # If wrap failed client_socket is the original.
                        # If wrap succeeded but handle_client failed, client_socket is null
                    # If we have a raw socket, close it
                    finally:
                        if ssl_client_socket != 1:
                            logging.warning(f"Closing SSL socket for {client_address} due to wrap/handle failure.")
                            try:
                                ssl_client_socket.close()
                            except socket.error as close_err:
                                logging.error(f"Error closing SSL socket for {client_address}: {close_err}")
                        elif client_socket and not ssl_client_socket:
                            logging.warning(f"Closing raw socket for {client_address} due to wrap/handle failure.")
                            try:
                                client_socket.close()
                            except socket.error as close_err:
                                logging.error(f"Error closing raw socket for {client_address}: {close_err}")
                        continue

                # If server timed out waiting for a connection, continue to wait for connections
                except socket.timeout:
                    continue
                # If server failed accepting for any other reason, log the error and continue to wait for connections
                except socket.error as accept_err:
                    logging.error(f"Error accepting connection: {accept_err}")
                    continue
                finally:
                    client_socket = None
                    client_address = None
                    ssl_client_socket = None
    # Terminate server on KeyboardInterrupt (Ctrl+C)
    except KeyboardInterrupt:
        executor.shutdown(wait=True)  # Wait for all threads to finish
        logging.info("Server shutdown (KeyboardInterrupt).")
    # Catch all in case of unexpected fatal error in program
    except Exception as outer_loop_e:
        logging.error(f"Fatal unexpected error in main server loop: {outer_loop_e}")
    finally:
        logging.info("Closing server socket.")
        server_socket.close()
        logging.info("Server stopped.")
        print('Server closed and stopped.')