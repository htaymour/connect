
import wexpect as pexpect
import time,sys
from cryptography.fernet import Fernet
import os,re

class User:
    def __init__(self, username, password=None):
        self.username = username
        self.password = password
        self.key = None

    # ---------- KEY MANAGEMENT ----------
    def generate_key(self):
        """Generate and save Fernet key (run once)."""
        key = Fernet.generate_key()
        with open("secret.key", "wb") as f:
            f.write(key)
        self.key = key

    def load_key(self):
        """Load existing key."""
        if not os.path.exists("secret.key"):
            print("[INFO] secret.key not found → generating new one")
            self.generate_key()

        with open("secret.key", "rb") as f:
            self.key = f.read()

    # ---------- ENCRYPT / DECRYPT ----------
    def encrypt_password(self, password):
        f = Fernet(self.key)
        return f.encrypt(password.encode())

    def decrypt_password(self, encrypted_password):
        f = Fernet(self.key)
        return f.decrypt(encrypted_password).decode()

    # ---------- STORAGE ----------
    def save_pass(self):
        self.load_key()

        if not self.password:
            self.password = input("Enter password: ")

        encrypted = self.encrypt_password(self.password)

        with open("cred.log", "wb") as f:
            f.write(encrypted)

        print("[OK] Password saved securely")

    def get_pass(self):
        self.load_key()

        if not os.path.exists("cred.log"):
            print("[INFO] No stored password → saving new one")
            self.save_pass()

        with open("cred.log", "rb") as f:
            encrypted = f.read()

        return self.decrypt_password(encrypted)

class Router:
    def __init__(self, name, username, password, route=None, policy=None, admin=None, interface=None, routes=None, vlan=None):
        self.name, self.username, self.password = name, username, password
        self.hostname = None
        self.route, self.policy, self.admin = route or {}, policy or {}, admin or {}
        self.interface, self.routes, self.vlan, self.child = interface or {}, routes or {}, vlan or {}, None

    def ssh(self, name, username, password):
        ssh_command = f"ssh -o HostKeyAlgorithms=+ssh-rsa -o PubkeyAcceptedAlgorithms=+ssh-rsa -o KexAlgorithms=+diffie-hellman-group14-sha1 -o MACs=+hmac-sha1 -o StrictHostKeyChecking=no {username}@{name}"
        self.child = pexpect.spawn(ssh_command, encoding='utf-8', timeout=200)
        self.child.logfile = sys.stdout
        while True:
            i = self.child.expect([r"[Pp]assword:", r"yes/no", r"[>#]", pexpect.TIMEOUT])
            if i == 0: self.child.sendline(password)
            elif i == 1: self.child.sendline("yes")
            elif i == 2: break
            else: self.child.sendline(password)
        self.child.sendline("enable")
        self.child.expect(r"[Pp]assword:", timeout=40)
        self.child.sendline(password)
        self.child.expect(r"#", timeout=40)
        self.child.sendline("term len 0")
        out = self.child.expect(r"#", timeout=40)
        self.hostname = self.child.before.splitlines()[-1].strip()
        print (self.hostname)
        self.child.logfile = None
        return True

    def push(self, cmd):
        if not self.child: print("Connection not established. Please connect first."); return None
        try: self.child.read_nonblocking(size=9999)
        except: pass
        self.child.sendline(cmd)
        time.sleep(0.5)
        self.child.expect(r'#', timeout=40)
        out = self.child.before
        out = re.sub(r'(Vl\d+)', r'\n\1', out)
        out = re.sub(r'(Gi\d+/\d+)', r'\n\1', out)
        out = re.sub(r'(Twe\d+/\d+/\d+)', r'\n\1', out)
        out = re.sub(r'(Te\d+/\d+/\d+)', r'\n\1', out)
        out = re.sub(r'(Hu\d+/\d+/\d+)', r'\n\1', out)
        out = re.sub(r'(Po\d+)', r'\n\1', out)
        out = re.sub(r'(Fa\d+/\d+)', r'\n\1', out)
        out = out.replace('\r\n','\n').replace('\r','\n')
        return out

    def discover(self):
        if not self.child: return
        self.interface.clear()
        self.routes.clear()
        self.vlan.clear()

        c = self.push("sh int desc")
        interfaces = {}
        for line in c.split("\n"):
            parts = line.split()
            if len(parts) >= 4:
                intf = parts[0]
                status = parts[1]
                proto = parts[2]
                desc = " ".join(parts[3:]).strip('"')
                if status == "up" and proto == "up" and desc:
                    interfaces[intf] = desc
        self.interface = interfaces

        vlans = self.push("sh vlan brief")
        vlans_dict = {}
        for m in re.finditer(r'(\d+)\s+([A-Za-z0-9\-_&./ ]+?)\s+(active|act/unsup|suspended)', vlans):
            vid = int(m.group(1))
            name = re.sub(r'^\d+\s+', '', m.group(2)).strip()
            if vid >= 10:
                vlans_dict[vid] = name
        self.vlan = vlans_dict

        sroutes = self.push("sh ip route")
        routes = {}

        for m in re.finditer(r'([A-Z\*]+)\s+(\d+\.\d+\.\d+\.\d+/\d+).+?via\s+(\d+\.\d+\.\d+\.\d+)', sroutes):
            route = m.group(2)
            nh = m.group(3)
            routes[route] = nh

        self.routes = routes

# Example usage
if __name__ == "__main__":
    h = User('<user ID>','')
    h.password = h.get_pass()
    router = Router(name='10.193.13.1',username = h.username,password = h.password)
    if (router.ssh(router.name,username = h.username,password = h.password )) : print ("connected to device")
    # Another method for connecting with local conneting script
    # router.nmstel(router.name)
    # router.push('en\nenablepassword')
    # time.sleep(2)
    # output = router.push('show ip int brief                                               ')
    # print(output)
    router.discover()
    print (router.interface)
    print (router.vlan)
    print(router.routes )
    #c = router.push("sh int desc")
    #print (c.splitlines()[1])
    # print only up interfaces with their IP addresses
    #print([interface +' ' + status[0] for interface, status in router.interface.items() if 'up' in status[1:]])
    #print (router.routes)
    # print default route 
    # print (router.routes['0.0.0.0/0'])
    # router.close_connection()
