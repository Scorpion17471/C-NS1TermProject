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
            client_address = None
            try:
                #-----Accept connection to client
                client_socket, client_address = server_socket.accept()
                print(f"Accepted connection from: {client_address}")

                #----------- Try to wrap socket with TLS and Handle
                try:
                    tls_client_socket = context.wrap_socket(client_socket, server_side=True)
                    client_socket = None
                    handle_client(tls_client_socket, client_address)
                except ssl.SSLError as ssl_e:
                    logging.error(f"SSL Handshake Error with {client_address}: {ssl_e}")
                    # client_socket is still the original unwrapped socket here.
                    # The finally block below WILL close it.
                except Exception as wrap_handle_e:
                    logging.error(f"Error during TLS wrap or handling for {client_address}: {wrap_handle_e}")
                    # If wrap failed client_socket is the original.
                    # If wrap succeeded but handle_client failed, client_socket is null
                finally:
                    if client_socket:
                        logging.warning(f"Closing raw socket for {client_address} due to wrap/handle failure.")
                        try:
                            client_socket.close()
                        except socket.error as close_err:
                            logging.error(f"Error closing raw socket for {client_address}: {close_err}")
            except socket.error as accept_err:
                logging.error(f"Error accepting connection: {accept_err}")
                continue
            except Exception as inner_loop_e:
                logging.error(f"Unexpected error in client handling loop for {client_address or 'Unknown'}: {inner_loop_e}")
                # Ensure cleanup if client_socket exists from accept() but failed before finally
                if client_socket:
                     try: client_socket.close()
                     except: pass # 
                continue # Continue to the next client connection attempt
    except KeyboardInterrupt:
        logging.info("Server shutdown (KeyboardInterrupt).")
    except Exception as outer_loop_e:
        logging.error(f"Fatal unexpected error in main server loop: {outer_loop_e}")
    finally:
        if server_socket:
            logging.info("Closing server socket.")
            server_socket.close()
            logging.info("Server stopped.")