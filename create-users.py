#!/usr/bin/python3

# INET4031
# Author: Edil Osman
# Date Created: 2025-11-12
# Date Last Modified: 2025-11-12
#
# Purpose:
# Read colon-delimited user records from STDIN (via input redirection) and
# for each valid line, construct the OS commands to:
#   1) create the user with a GECOS string (full name),
#   2) set the user's password, and
#   3) add the user to any requested groups.
#
# Dry-run vs. real-run:
#   - For a dry-run, keep all os.system(...) calls commented out and only print the commands.
#   - For a real run, uncomment the os.system(...) lines so commands actually execute.

import os   # used to invoke shell commands with os.system(...)
import re   # used to detect comment/skip lines with a regular expression
import sys  # used to read input lines from standard input (sys.stdin)

def main():
    for line in sys.stdin:
        # Skip lines that begin with '#' (treated as comments / disabled entries in the input file).
        # The script uses this to allow “skip this user” markers without deleting the line.
        match = re.match(r"^#", line)

        # Split the input line into fields separated by ':'.
        # Expected layout: username:password:last:first:group_list
        fields = line.strip().split(':')

        # Validate the record:
        # - If the line is a comment (match is not None), skip it.
        # - If the record doesn’t have exactly 5 fields, skip it (prevents crashes on bad data).
        # This relies on the match check above and the result of the split we just did.
        if match or len(fields) != 5:
            continue

        # Map fields into variables and format a GECOS string.
        # /etc/passwd stores the “gecos” field for human-friendly info. Here we put "First Last,,,"
        # so that the account has a full name visible in tools that read gecos.
        username = fields[0]
        password = fields[1]
        gecos = "%s %s,,," % (fields[3], fields[2])   # first last,,,

        # The 5th field is a comma-delimited list of groups. A single '-' means “no extra groups”.
        groups = fields[4].split(',')

        # 1) Create the user account with --disabled-password (we will set the password next)
        #    and attach the GECOS string.
        print("==> Creating account for %s..." % (username))
        cmd = "/usr/sbin/adduser --disabled-password --gecos '%s' %s" % (gecos, username)
        # DRY-RUN: keep the next line commented so we only print the command
        # REAL-RUN: uncomment the next line so the command executes
        # os.system(cmd)

        # 2) Set the user’s password by piping two lines (password + password) into passwd.
        #    This mirrors an interactive password change non-interactively.
        print("==> Setting the password for %s..." % (username))
        cmd = "/bin/echo -ne '%s\n%s' | /usr/bin/sudo /usr/bin/passwd %s" % (password, password, username)
        # DRY-RUN: keep commented
        # REAL-RUN: uncomment to execute
        # os.system(cmd)

        # 3) Process supplemental groups. If the group token is '-', skip adding to groups.
        for group in groups:
            # Only add the user to a group when the token is not the sentinel '-'.
            if group != '-':
                print("==> Assigning %s to the %s group..." % (username, group))
                cmd = "/usr/sbin/adduser %s %s" % (username, group)
                # DRY-RUN: keep commented
                # REAL-RUN: uncomment to execute
                # os.system(cmd)

if __name__ == '__main__':
    main()
