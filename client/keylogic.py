import os

from Crypto.PublicKey import RSA

def generate_key_pair(password: str):
    """
    Generate a public/private RSA key pair.
    
    Args:
        bits (int): The size of the key in bits. Default is 2048.
    
    Returns:
        tuple: A tuple containing the private key and public key as PEM strings.
    """
    print(f"Your new RSA Key Password is: {password}")
    print("Save it now as it will no longer be visible.")
    input("Press Enter to continue...")
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
    
    # Generate RSA key pair
    key = RSA.generate(2048)
    
    # Export the private key in PEM format
    try:
        with open('./keys/private.pem', 'wb') as f:
            f.write(key.export_key(passphrase=password, pkcs=8, protection="PBKDF2WithHMAC-SHA512AndAES256-CBC", prot_params={'iteration_count':21000}))
        
        # Export the public key in PEM format
        with open('./keys/public.pem', 'wb') as f:
            f.write(key.publickey().export_key())
    except Exception as e:
        print(f"Error during key creation: {e}")
        return None
    else:
        print("Key pair generated and saved successfully.")
        return True

# Retrieve the private key from the file if it exists
def get_private():
    """
    Retrieve the private key from the file.
    """
    # Prompt for password to decrypt the private key, attempt 3 times, then fail
    i = 3
    while i > 0:
        try:
            return RSA.import_key(open("./keys/private.pem").read(), input("Enter RSA Key password: "))
        except (FileNotFoundError) as e:
            print(f"Error retrieving private key: {e}")
            break
        except (ValueError, TypeError, IndexError) as e:
            print(f"Error retrieving private key: {e}")
            i -= 1
            print(f"Attempts remaining: {i}")
    print("Failed to retrieve private key after 3 attempts.") if i == 0 else print(f"Failed to retrieve private key - File not found.")
    return None

# Retrieve the public key from the file if it exists
def get_public():
    """
    Retrieve the public key from the file.
    """
    try:
        return RSA.import_key(open("./keys/public.pem").read())
    except (FileNotFoundError) as e:
        print(f"Error retrieving public key - File not found: {e}")
        return None

def get_publics():
    """
    Retrieve the public key from the file.
    """
    try:
        return open("./keys/public.pem").read()
    except (FileNotFoundError) as e:
        print(f"Error retrieving public key - File not found: {e}")
        return None