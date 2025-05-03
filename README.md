# C-NS1TermProject
Secure File Transfer application with login based access.

# Virtual Environment
To create an environment to run the program, use ```python3 -m venv .venv```

To launch the environment run ```source .venv/bin/activate``` for Unix/Max or ```.venv/bin/activate``` in PowerShell for Windows

From there, you can use the provided "requirements.txt" file to install dependencies using the command ```python -m pip install -r requirements.txt```

# Server
To generate certificate/private key for the server, run ```openssl req -x509 -newkey rsa:4096 -keyout serverr.pem -out cert.pem -sha256 -days 365``` and place the created "serverr.pem" and "cert.pem" into the server's "certs" folder

Run the server using ```python main.py``` from within the server folder

It will run indefinitely unless given a KeyboardInterrupt (CTRL + C is default for VSCode)

# Client
With the server active, run the client program from within the client folder using ```python main.py``` to connect to the server

Initial launch will create an RSA private/public key pair and generate a pseudorandom password to secure it that you should save

Successive launches will require the generated password, failure to provide 3 times in a row, will cause the program to delete and regenerate entirely new keys

  ## Actions (Logged Out):
  - Register
  - Login
  - Exit

  ## Actions (Logged In):
  - Add Friend
  - Remove Friend
  - Show Online Friends
  - Send File
  - Logout