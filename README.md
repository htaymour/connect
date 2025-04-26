# Connect Package

## Overview
The **Connect** package is a Python library designed for managing network devices through SSH. It provides functionalities for securely storing and retrieving passwords, managing network automation making it an ideal solution for automating network management tasks across various devices.

## Features
- **SSH Connectivity**: Establish SSH connections to any network device.
- **Password Encryption**: Securely encrypt and store passwords for safe access.
- **Device Discovery**: Retrieve and display interfaces and routing information.
- **Command Execution**: Execute commands on network devices and retrieve output.

## Requirements
- Python 3.x
- `pexpect` library
- `cryptography` library

You can install the required libraries using pip:
```bash
pip install pexpect cryptography
```

## Installation
Clone this repository to your local machine:
```bash
git clone https://github.com/htaymour/connect.git
cd connect
```

## Usage

### Importing the Package
You can import the `User` and `Router` classes in your own scripts to facilitate network automation:
```python
from connect import User, Router
```

### Creating a User Instance
Instantiate the `User` class with a username and password:
```python
h = User('your_username', 'your_password')
```

### Generating and Loading a Key
Generate a Fernet key for encrypting passwords:
```python
h.generate_key()  # Generates and saves a key to secret.key
h.load_key()      # Loads the key from the file
```

### Saving an Encrypted Password
To save an encrypted password, call:
```python
h.save_pass()  # Prompts for password and saves it to cred.log
```

### Retrieving and Decrypting Password
Retrieve and decrypt the stored password using:
```python
h.get_pass()  # Returns the decrypted password
```

### Creating a Network Device Instance
Create a network device instance with the device's IP, username, and password:
```python
device = Router(name='device_ip', h.username, h.password)
# or you can use a special username and password in case required a special logon
device = Router(name='device_ip', username='your_username', password='your_password')
```

### Connecting to the Device
Connect to the network device using SSH:
```python
if device.ssh(device.name): print("Connected to device")
```

### Executing Commands
Execute commands on the network device:
```python
output = device.push('show ip int brief')
print(output)
```

### Discovering Interfaces and Routes
Discover interfaces and static routes:
```python
device.discover()
```

### Printing Up Interfaces
Print interfaces that are "up" along with their IP addresses:
```python
print([interface + ' ' + status[0] for interface, status in device.interface.items() if 'up' in status[1:]])
```

### Closing the Connection
Close the SSH connection:
```python
device.close_connection()
```

## Example
Here’s a complete example of how to use the package:
```python
if __name__ == "__main__":
    h = User('your_username', '')
    h.password = h.get_pass()
    device = Router(name='device_ip', username=h.username, password=h.password)
    if device.ssh(device.name, username=h.username, password=h.password):
        print("Connected to device")
    output = device.push('show ip int brief')
    print(output)
    device.discover()
    # print only up interfaces along with their IP address
    print([interface + ' ' + status[0] for interface, status in device.interface.items() if 'up' in status[1:]])
    # print router routes
    print(device.routes)
    # print default route next hop
    print(device.routes['0.0.0.0/0'])
    device.close_connection()
```

## Security
The Connect package ensures that sensitive information, such as passwords, is securely encrypted and stored. The encryption is handled using the `cryptography` library, providing a robust method for protecting credentials.

## Contribution
Feel free to fork the repository and submit pull requests for any improvements or additional features.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For any questions or issues, please open an issue in the repository or contact the author.

---

This README provides a comprehensive guide for using the Connect package, highlighting its capabilities for managing various network devices and securely handling passwords.
