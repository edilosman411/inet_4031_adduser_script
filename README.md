# INET4031 – Automated Linux User Creation

### Description
This Python 3 script automates adding multiple users and groups on an Ubuntu server.  
It reads a colon-delimited text file (`create-users.input`) that lists usernames, passwords, names, and groups, then builds and executes the necessary system commands.

### How It Works
1. Each line in the input file follows this format:
username:password:last:first:group1,group2

2. Lines beginning with `#` are skipped (used for comments or disabled users).  
3. Lines missing any required fields are ignored.  
4. For each valid line, the script:
- Creates the account with `adduser`
- Sets the password with `passwd`
- Assigns the user to any groups listed

---

### Running the Script
**Dry Run (prints commands only)**  
```bash
./create-users.py < create-users.input

**Real Run (executes user creation):  
sudo ./create-users.py < create-users.input

##*After a successful run, confirm users and group memberships:

grep user0 /etc/passwd
grep user0 /etc/group

##Expected output will look similar to:

user01:x:1001:1001:First01 Last01,,,:/home/user01:/bin/bash
user02:x:1002:1002:First02 Last02,,,:/home/user02:/bin/bash
group01:x:1003:user01
group02:x:1004:user02
