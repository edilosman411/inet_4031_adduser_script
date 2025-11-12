#!/usr/bin/python3
# INET4031 – Automated Linux User Creation (Dry-Run Toggle Version)
# Author: Edil Osman
# Date: 2025-11-12
#
# Purpose:
# This Python 3 script automates adding multiple users and groups on an Ubuntu server.
# It reads a colon-delimited text file (create-users.input) and creates accounts,
# sets passwords, and assigns users to groups.  This version adds an interactive
# “dry-run” toggle so the admin can preview commands before running them for real.

import os
import re
import sys

# ----- Ask user whether to dry-run (read from terminal, not stdin) -----
def get_dry_setting():
    # Allow environment override: DRY_RUN=Y or DRY_RUN=N
    env = os.environ.get("DRY_RUN", "").strip().upper()
    if env in ("Y", "N"):
        return env

    # Read from controlling terminal (so '< file' redirection won't block input)
    try:
        with open("/dev/tty") as tty:
            while True:
                print("Run in DRY-RUN mode (Y/N)? ", end="", flush=True)
                ans = tty.readline()
                if not ans:
                    return "Y"      # default to safe mode if EOF
                ans = ans.strip().upper()
                if ans in ("Y", "N"):
                    return ans
    except Exception:
        return "Y"  # fallback to safe dry-run

dry = get_dry_setting()

# Wrapper to either print or execute shell commands
def run_cmd(cmd: str) -> int:
    """Print command in dry-run mode; execute it in real mode."""
    if dry == "Y":
        print(f"DRY-RUN: {cmd}")
        return 0
    return os.system(cmd)

def main():
    for raw in sys.stdin:
        line = raw.rstrip("\n")

        # Skip comment lines starting with '#'
        match = re.match(r"^#", line)

        # Split colon-separated fields
        fields = line.strip().split(':')

        # If it's a comment or malformed, skip (and show messages in dry-run)
        if match or len(fields) != 5:
            if dry == "Y":
                if match:
                    print(f"DRY-RUN SKIP (comment): {line.strip()}")
                elif line.strip():
                    print(f"DRY-RUN ERROR (bad line, need 5 fields): {line.strip()}")
            continue

        # Extract field values
        username = fields[0]
        password = fields[1]
        gecos = f"{fields[3]} {fields[2]},,,"   # Full name, room, etc.
        groups = fields[4].split(',')

        # Step 1 – Create user account
        print(f"==> Creating account for {username}...")
        cmd = f"/usr/sbin/adduser --disabled-password --gecos '{gecos}' {username}"
        run_cmd(cmd)

        # Step 2 – Set password
        print(f"==> Setting the password for {username}...")
        cmd = f"/bin/echo -ne '{password}\\n{password}' | /usr/bin/sudo /usr/bin/passwd {username}"
        run_cmd(cmd)

        # Step 3 – Add to supplemental groups
        for group in groups:
            if group != '-':
                print(f"==> Assigning {username} to the {group} group...")
                cmd = f"/usr/sbin/adduser {username} {group}"
                run_cmd(cmd)

if __name__ == '__main__':
    main()

