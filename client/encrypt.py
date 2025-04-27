import base64
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from cconnector import send_message, receive_message
import json, os
import traceback

AES_KEY_SIZE = 32 #256 bits
AES_NONCE_SIZE = 12 #96 bits

def encrypt_file(tls_socket, data, file_name):
    
    pubkey = ''
    
    # 1. Get public key
    senddata = {
        "action": "getpk",
        "username": input("Enter the recipient you wish to send to: ")
    }
    message = json.dumps(senddata)
    send_message(tls_socket, message) 
    response = receive_message(tls_socket, None)
    message_r = json.loads(response)
    if message_r["status"] == "ERROR":
        print(message_r["message"])
        return 0
    else:
        print(f"Response received {response}")
        pubkey = message_r['key']
        try:
            # Try loading and re-exporting to verify its format and content
            temp_pub_key = RSA.import_key(pubkey)
            re_exported_pub_key = temp_pub_key.export_key().decode()
            # print(f"DEBUG: Verified and Re-exported Retrieved Public Key:\n{re_exported_pub_key}")
        except Exception as e_pub:
            print(f"DEBUG: Error validating/re-exporting retrieved public key: {e_pub}")
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
    return ({
        "action": "upload",
        "recipient": senddata["username"],
        "file": file_name,
        "nonce_b64": base64.b64encode(nonce).decode('utf-8'),
        "encrypted_file_b64": base64.b64encode(ciphertext).decode('utf-8'),
        "tag_b64": base64.b64encode(tag).decode('utf-8'), # Send tag separately for clarity at receiver
        "encrypted_key_b64": base64.b64encode(encrypted_session_key).decode('utf-8')
    })


def decrypt_file(tls_socket, payload) : # payload is the nested 'message' dict
    private_key_obj = None # Initialize
    private_key_path = './keys/private.pem'
    passphrase = input("Enter RSA Key password: ")
    try:
        with open(private_key_path, 'r') as f:
            pem_data = f.read()
        key_obj = RSA.import_key(pem_data, passphrase=passphrase)
        print(f"SUCCESS: Private key loaded successfully.")
    # Optional: Check if it can export its public key
        pub_key_pem = key_obj.publickey().export_key().decode()
        print("Successfully exported corresponding public key:")
        print(pub_key_pem)
    except Exception as e_exp:
         print(f"Could not export public key from loaded private key: {e_exp}")
    try:
        print("Decoding received data")
        # Decode Base64 data
        nonce_str = payload['nonce_b64']
        nonce = base64.b64decode(nonce_str.encode('ascii'))

        encrypted_file_str = payload['encrypted_file_b64']
        encrypted_file_bytes = base64.b64decode(encrypted_file_str.encode('ascii'))

        tag_str = payload['tag_b64']
        tag = base64.b64decode(tag_str.encode('ascii'))

        encrypted_key_str = payload['encrypted_key_b64']
        encrypted_session_key_bytes = base64.b64decode(encrypted_key_str.encode('ascii'))

        # Decrypt session key using same PKCS1 padding as encryption 
        print("Decrypting session key...")
        rsa_cipher = PKCS1_OAEP.new(key_obj)
        session_key = rsa_cipher.decrypt(encrypted_session_key_bytes) 
        print(f"Successfully decrypted Session key")

        # Decrypt file and return
        print("Decrypting file content...")
        aes_cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
        decrypted_data = aes_cipher.decrypt_and_verify(encrypted_file_bytes, tag)
        print("File content successfully decrypted and verified.")

        return decrypted_data

    except KeyError as e:
        print(f"Error decrypting: Missing expected key in payload: {e}")
        return None
    except ValueError as e:
        # This catches "Incorrect decryption.", "MAC check failed", etc.
        print(f"DECRYPTION FAILED (ValueError): Likely incorrect key/passphrase/padding OR corrupted data. Details: {e}")
        traceback.print_exc() # See exactly where it happened (RSA or AES step)
        return None
    except Exception as e:
        print(f"An unexpected error occurred during decryption: {e}")
        traceback.print_exc()
        return None