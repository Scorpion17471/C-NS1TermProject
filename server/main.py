# server/main.py
import sys
import os

from server import run_server


def main():

    print("--- Initializing Server ---")
    HOST = '127.0.0.1'  # Listen on localhost
    PORT = 8443         # Port number to listen on

    print(f"Configuration: Host={HOST}, Port={PORT}")

    run_server(HOST, PORT, "./certs/cert.pem", "./certs/serverr.pem")

if __name__ == "__main__":
    main()