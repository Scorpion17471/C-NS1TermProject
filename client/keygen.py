from Crypto.PublicKey import RSA

def generate_key_pair(password):
    """
    Generate a public/private RSA key pair.
    
    Args:
        bits (int): The size of the key in bits. Default is 2048.
    
    Returns:
        tuple: A tuple containing the private key and public key as PEM strings.
    """
    print(f"Your Password is: {password}")
    print(f"Save it now as it will no longer be visible.")
    input("Press Enter to continue...")

    # Set the key size
    bits=2048
    
    # Generate RSA key pair
    key = RSA.generate(bits)
    
    # Export the private key in PEM format
    private_key = key.export_key()
    
    # Export the public key in PEM format
    public_key = key.publickey().export_key()
    
    return private_key, public_key