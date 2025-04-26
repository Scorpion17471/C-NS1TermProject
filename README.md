# C-NS1TermProject
Secure File Transfer application with login based access.

# Server
Run the server using ```python main.py``` from within the server folder
It will run indefinitely unless given a KeyboardInterrupt (CTRL + C is default for VSCode)

To generate certificates for the server, run: ```openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 365```

# Client
With the server active, run the client program from within the client folder using ```python main.py``` to connect to the server

  ## Actions (Logged Out):
  - Register
  - Login
  - Exit

  ## Actions (Logged In):
  - Add Friend
  - Remove Friend
  - Show Online Friends
  - Send DM (WIP)
  - Send File (WIP)
  - Logout
