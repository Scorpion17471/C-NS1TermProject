import sys
import os

from server import run_server # Assuming server package is structured correctly

def main():
    print("--- Initializing Server ---")
    HOST = '127.0.0.1'  # Listen on localhost
    PORT = 8443         # Port number to listen on

    print(f"Configuration: Host={HOST}, Port={PORT}")
    print("Current Working Directory:", os.getcwd()) # Keep this for debugging

    # Construct the absolute path to the certs directory relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    certs_dir = os.path.join(script_dir, "certs")
    cert_path = os.path.join(certs_dir, "cert.pem")
    key_path = os.path.join(certs_dir, "serverr.pem") # Assuming serverr.pem is the key

    print("Looking for cert at:", cert_path)
    print("Looking for key at:", key_path)

    # Add checks to see if the files exist (optional but recommended)
    if not os.path.exists(cert_path):
        print(f"Error: Certificate file not found at {cert_path}")
        sys.exit(1)
    if not os.path.exists(key_path):
         print(f"Error: Key file not found at {key_path}")
         sys.exit(1)

    run_server(HOST, PORT, cert_path, key_path)

if __name__ == "__main__":
    main()