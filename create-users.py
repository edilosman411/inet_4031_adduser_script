#!/usr/bin/python3
# INET4031  –  Automated Linux User Creation
# Author: Edil Osman
# Date Created: 2025-11-12
# Last Modified: 2025-11-12
#
# Description:
# Reads colon-delimited user records from STDIN and, for each valid record,
# builds the system commands needed to:
#   1) create the account,
#   2) set the password, and
#   3) assign group memberships.
#
# Dry-run mode:
#   • Keep os.system(...) lines commented to only print commands.
# Real-run mode:
#   • Uncomment os.system(...) lines so commands actually execute.

import os    # to run Linux shell commands
import re    # to detect comment lines that start with '#'
import sys   # to read each line piped in from create-users.input

def main():
    for line in sys.stdin:
        # Skip comment lines beginning with '#'
        match = re.match(r"^#", line)

        # Split the line into fields: username:password:last:first:groups
        fields = line.strip().split(':')

        # Skip any invalid or incomplete line (not exactly 5 fields)
        if match or len(fields) != 5:
            continue

        # Extract user info and format the GECOS string
        username = fields[0]
        password = fields[1]
        gecos = "%s %s,,," % (fields[3], fields[2])   # first last

        # Parse comma-separated group list; '-' means “no extra groups”
        groups = fields[4].split(',')

        # Step 1 – create user account
        print(f"==> Creating account for {username}...")
        cmd = f"/usr/sbin/adduser --disabled-password --gecos '{gecos}' {username}"
        # os.system(cmd)   # Uncomment for real run

        # Step 2 – set password
        print(f"==> Setting the password for {username}...")
        cmd = f"/bin/echo -ne '{password}\\n{password}' | /usr/bin/sudo /usr/bin/passwd {username}"
        # os.system(cmd)   # Uncomment for real run

        # Step 3 – assign to groups (if any)
        for group in groups:
            if group != '-':   # skip placeholder
                print(f"==> Assigning {username} to the {group} group...")
                cmd = f"/usr/sbin/adduser {username} {group}"
                # os.system(cmd)   # Uncomment for real run

if __name__ == '__main__':
    main()

