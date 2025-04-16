import base64
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from cconnector import send_message, receive_message
import json, os

AES_KEY_SIZE = 32 #256 bits
AES_NONCE_SIZE = 12 #96 bits

def send_file(tls_socket):
    data = b'encrypted data'
    pubkey = ''
    file_name = input("Please enter the name of the file you'd like to send: ")
    # 1. Get public key
    senddata = {
        "action": "getpk",
        "username": input("Enter the recipient you wish to send to: ")
    }
    message = json.dumps(senddata)
    try:
        send_message(tls_socket, message) 
        response = receive_message(tls_socket, None)
        message_r = json.loads(response)
        pubkey = message_r['key']
       # print(f"user's public key: '{pubkey}'")       #For testing
    except Exception as e:
        print(f"Error retrieving client's public key: '{e}'")
        input("Returning to menu, press Enter to continue...")
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
    except json.JSONDecodeError:
            print("Invalid JSON format in response, please try again.")
            return
    # 2. Generate Session Key
    session_key = get_random_bytes(AES_KEY_SIZE)
    # 3. Create RSA cipher using recipients public key
    rsa_key_obj = RSA.import_key(pubkey)
    rsa_cipher = PKCS1_OAEP.new(rsa_key_obj)
    encrypted_session_key = rsa_cipher.encrypt(session_key)
    # 4. Use session key to encrypt file
    aes_cipher = AES.new(session_key, AES.MODE_GCM)
    nonce = aes_cipher.nonce
    ciphertext, tag = aes_cipher.encrypt_and_digest(data)
    # 5. Send the payload
    payload = {
        "action": "upload",
        "file": file_name,
        "nonce_b64": base64.b64encode(nonce).decode('utf-8'),
        "encrypted_file_b64": base64.b64encode(ciphertext).decode('utf-8'),
        "tag_b64": base64.b64encode(tag).decode('utf-8'), # Send tag separately for clarity at receiver
        "encrypted_key_b64": base64.b64encode(encrypted_session_key).decode('utf-8')
    }
    message = json.dumps(payload)
    try:
        send_message(tls_socket, message)
        response = receive_message(tls_socket, None)
        if response is not None:
            try:
                data = json.loads(response)  # Parse incoming JSON message
            except json.JSONDecodeError:
                print("Invalid JSON format in response, please try again.")
                return
            # Print server response
            if data["status"] == "ERROR":
                print(f"\nRegistration failed: {data["message"]}")
            elif data["status"] == "OK":
                print(f"\n{data["message"]}")
                # Save account details, send server public key
            # Return to client menu
            input("Returning to menu, press Enter to continue...")

        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
    except Exception as e:
         print("Error in /client/encrypt.py")
         
