# server/main.py
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added project root to Python path: {project_root}")
try:
    from server.listener import start_listener
except ImportError as e:
    print(f"Error importing start_listening: {e}")
    print("Make sure server/listener.py exists and the path setup is correct.")
    sys.exit(1) # Exit if we can't import the core listener function



def main():

    print("--- Initializing Server ---")
    HOST = '127.0.0.1'  # Listen on localhost
    PORT = 8443         # Port number to listen on

    print(f"Configuration: Host={HOST}, Port={PORT}")

    start_listener(HOST, PORT, "certs/cert.pem", "certs/serverr.pem")

if __name__ == "__main__":
    main()