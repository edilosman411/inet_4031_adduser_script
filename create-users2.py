#!/usr/bin/python3
# INET4031 – Automated Linux User Creation (dry-run toggle version)
# Author: Edil Osman
# Date: 2025-11-12
#
# Reads colon-delimited user records from STDIN:
#   username:password:last:first:group1,group2
# Skips lines that start with '#'. Ignores lines not having exactly 5 fields.
#
# DRY-RUN TOGGLE:
#   • Prompts: "Run in DRY-RUN mode (Y/N)?"
#   • If Y: print the OS commands that would run; also print notes for bad/skip lines.
#   • If N: actually execute the OS commands; stay quiet on bad/skip lines.

import os
import re
import sys

# ----- Ask user whether to dry-run -----
dry = None
while dry not in ("Y", "N"):
    try:
        dry = input("Run in DRY-RUN mode (Y/N)? ").strip().upper()
    except EOFError:
        # If input is redirected and prompt can't read (e.g., CI), default to safe DRY-RUN
        dry = "Y"

def run_cmd(cmd: str) -> int:
    """Execute or print the command depending on dry-run setting."""
    if dry == "Y":
        print(f"DRY-RUN: {cmd}")
        return 0
    return os.system(cmd)

def main():
    for raw in sys.stdin:
        line = raw.rstrip("\n")

        # Skip comment lines using '#' at column 0
        is_comment = re.match(r"^#", line) is not None

        # Expect: username:password:last:first:groups
        fields = line.strip().split(':')

        # Validate/skip
        if is_comment or len(fields) != 5:
            if dry == "Y":
                if is_comment:
                    print(f"DRY-RUN SKIP (comment): {line}")
                elif line.strip():
                    print(f"DRY-RUN ERROR (bad line, need 5 fields): {line}")
            continue

        username = fields[0]
        password = fields[1]
        # GECOS field for /etc/passwd ("First Last,,,")
        gecos = f"{fields[3]} {fields[2]},,,"

        # Comma-separated list of groups; '-' means no extra groups
        groups = fields[4].split(',')

        # 1) Create user (password disabled here; set next)
        print(f"==> Creating account for {username}...")
        cmd = f"/usr/sbin/adduser --disabled-password --gecos '{gecos}' {username}"
        run_cmd(cmd)

        # 2) Set password (non-interactive)
        print(f"==> Setting the password for {username}...")
        cmd = f"/bin/echo -ne '{password}\\n{password}' | /usr/bin/sudo /usr/bin/passwd {username}"
        run_cmd(cmd)

        # 3) Add to supplemental groups
        for group in groups:
            if group != '-':
                print(f"==> Assigning {username} to the {group} group...")
                cmd = f"/usr/sbin/adduser {username} {group}"
                run_cmd(cmd)

if __name__ == '__main__':
    main()

