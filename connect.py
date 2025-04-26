import pexpect
import time
from cryptography.fernet import Fernet
class user (): 
    def __init__(self, username , password):
        self.username = username if username else None
        self.password = password if password else None
        self.key = ''
    def generate_key(self):
        """Generates a new Fernet key and saves it to a file."""
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    def encrypt_password(self,password, key):
        """Encrypts a password using the provided key."""
        f = Fernet(key)
        encrypted_password = f.encrypt(password.encode())
        return encrypted_password.decode()
    def decrypt_password(self,encrypted_password, key):
        """Decrypts an encrypted password using the provided key."""
        f = Fernet(key)
        decrypted_password = f.decrypt(encrypted_password.encode()).decode()
        return decrypted_password
        # --- Example Usage --- 
    def generate_key(self):
        # 1. Generate a key (only do this once)
        self.key = self.generate_key() 
    def load_key (self):
        # 2. Load the key
        with open("secret.key", "rb") as key_file:
            self.key = key_file.read()
    def save_pass(self):
        # 3. Encrypt and store the password
        self.password = raw_input("your password ")
        self.encrypted_password = self.encrypt_password(self.password, self.key)
        print("Encrypted Password: " + self.encrypted_password)
        with open("cred.log", "wb") as password_file:
            password_file.write(self.encrypted_password)
    def decrypt_pass(self):
        # 4. Retrieve and decrypt the password
        self.decrypted_password = self.decrypt_password(self.encrypted_password, self.key)
        print("Decrypted Password: " + self.decrypted_password)
    def get_pass(self):
        # 5. to use the password
        with open("secret.key", "rb") as key_file:
            self.key = key_file.read()
        with open("cred.log", "rb") as key_file:
            encrypted_password = key_file.read()
        self.decrypted_password = self.decrypt_password(encrypted_password, self.key)
        # print (self.decrypted_password)
        return (self.decrypted_password)

class Router:
    def __init__(self, name,username , password, route=None, policy=None, admin=None, interface=None, routes = None):
        self.name = name
        self.username = username if username else None
        self.password = password if password else None
        self.route = route if route is not None else {}
        self.policy = policy if policy is not None else {}
        self.admin = admin if admin is not None else {}
        self.interface = interface if interface is not None else {}
        self.routes = routes if routes is not None else {}
        self.child = None    
    def ssh(self,name,username,password) :  
        #try:
        # Add -o StrictHostKeyChecking=no to the SSH command
        ssh_command = "ssh -o StrictHostKeyChecking=no " + username + "@" + name
        self.child = pexpect.spawn(ssh_command)
        # Wait for the password prompt and send the password
        time.sleep(3)
        self.child.sendline(password)
        time.sleep(1)
        # Wait for the shell prompt
        self.child.expect(["#",">"])  # Adjust based on the actual prompt
        out = self.child.before.decode('ascii')
        print(out)
        return out
        # except Exception as e:
        #     print("Connection not established correctly. Please make sure the IP is correct and authenticate the server before running.")
        #     print("Error:", e)
        #     if self.child:
        #         self.close_connection()
    def nmstel(self,name) :  
        # try:
        out = None
        ssh_command = "nmstel " + name
        self.child = pexpect.spawn(ssh_command)
        time.sleep(5)
        # Wait for the password prompt and send the password
        while True:
            index = self.child.expect([r'#', r'assword:',r'sername:'])  # Adjust based on the actual prompt
            out = self.child.before.decode('ascii')
            print (out)
            if index == 1:  # Found "asswprd"
                self.child.send(self.password)  # Send a space to continue
                time.sleep(3)
            elif index == 2:  # Found "sername"
                self.child.send(self.username)  # Send a space to continue
                time.sleep(3)
            else : 
                out = self.child.before.decode('ascii')
                return out
        # except Exception as e:
        #     print("Connection not established correctly. Please make sure the IP is correct and authenticate the server before running.")
        #     print("Error:", e)
        #     if self.child:
        #         self.close_connection()
    def push(self, cmd):
        out = []
        if self.child:
            self.child.sendline(cmd)
            time.sleep(len(cmd) / 50 + 0.5)
            while True:
                index = self.child.expect([r'#', r'--More--'])
                if index == 0:  # Found "#"
                    out += self.child.before.decode('ascii').split('\n')[0:-2]
                    break  # Exit the loop if "#" is found
                elif index == 1:  # Found "--More--"
                    out += self.child.before.decode('ascii').split('\n')[0:-2]
                    self.child.send(' ')  # Send a space to continue
                    time.sleep(len(cmd) / 50 + 0.5)
            result = []
            for x in out:
                if self.name.upper() + " (global) $" in x: continue
                if "Command fail" in x: continue
                if "error " in x: continue
                if "end " in x: continue
                if "Unknown action" in x: continue
                if cmd in x: continue
                if 'More' in x : continue
                else:
                    result.append(x)
            return "\n".join(result)
        else:
            print("Connection not established. Please connect first.")
            return None
    def discover(self): 
            if self.child:
                cmd = "sh ip int brief"
                ints = self.push(cmd)
                for x in ints.split('\n')[1:]:
                    line = [word.strip('\n').encode('utf-8') for word in x.split(' ') if word]
                    self.interface[line[0]] = [line[1] , line[4], line[5] ]
                cmd = "sh ip route static"
                sroutes = self.push(cmd)
                for x in sroutes.split('\n'):
                    if 'via' in x :
                        subnet =  x.split('via')[0].split(r'[')[0].replace('S', '').replace('*', '').strip().encode('utf-8')
                        getw = x.split ('via')[1].strip().encode('utf-8') 
                        self.routes[subnet] = getw
            else : return
    def close_connection(self):
        if self.child:
            self.child.sendline('exit')
            self.child.close()
            print("Connection closed.")

            
# Example usage
if __name__ == "__main__":
    h = user('htaymour','')
    h.password = h.get_pass()
    router = Router(name='10.71.100.44',username = h.username,password = h.password)
    if (router.ssh(router.name,username = h.username,password = h.password )) : print ("connected to device")
    # Another method for connecting with local conneting script
    # router.nmstel(router.name)
    # router.push('en\nenablepassword')
    output = router.push('show ip int brief                                               ')
    print(output)
    router.discover()
    print (router.interface)
    # print only up interfaces with their IP addresses
    print([interface +' ' + status[0] for interface, status in router.interface.items() if 'up' in status[1:]])
    print (router.routes)
    # print default route 
    # print (router.routes['0.0.0.0/0'])
    router.close_connection()
