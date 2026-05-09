#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import hashlib
import os
import sys
import fcntl

def check_for_existing_instance(lock_file):
    """
    Checks if another instance of the script is already running by attempting to acquire a lock on the lock file.
    If the lock cannot be acquired, then another instance of the script is already running.

    :param lock_file: path to the lock file
    :return: True if another instance of the script is already running, False otherwise
    """
    # Try to open the lock file in write mode
    try:
        fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY | os.O_EXCL)
    except FileExistsError:
        # File already exists, so another instance of the script is already running
        return True

    # Lock the file
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        # Another process already holds the lock, so another instance of the script is already running
        return True


lock_file = '/tmp/kernel-update-check.pid'

if check_for_existing_instance(lock_file):
    print('Another instance of the script is already running.')
    sys.exit(1)

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
print("change dir to: "+CURRENT_DIR)
os.chdir(CURRENT_DIR)

# URL of the kernel.org page with the update table
url = "https://www.kernel.org/"

# Directory to store the hash file
hash_dir = "/tmp/"

# File to store the last hash value and wait number
hash_file = os.path.join(hash_dir, "kernel_org_hash")

def updating_gentoo_kernels():
    os.system("python update_packages.py")
    #os.system("python push_changes.py")

# Read in the last hash value and wait number from the file
try:
    with open(hash_file, "r") as f:
        last_hash, wait_number = f.read().strip().split(",")
        wait_number = int(wait_number)
except FileNotFoundError:
    last_hash, wait_number = None, 0


try:
    # Send an HTTP request to the website and get the response
    response = requests.get(url)

    # Use BeautifulSoup to parse the HTML content of the response
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table that lists the latest kernel versions
    table = soup.find("table", attrs={"id": "releases"})

    # Remove the 'linux-next' row from the table
    for row in table.find_all("tr"):
        if "linux-next:" in str(row):
            row.decompose()

    # Get the HTML content of the table
    table_html = str(table)

    # Hash the HTML content of the table
    hash_value = hashlib.md5(table_html.encode()).hexdigest()

    if last_hash is None or hash_value != last_hash:
        # There are updates available on kernel.org!
        print("There are updates available on kernel.org!")
        updating_gentoo_kernels()
        last_hash = hash_value
        wait_number = 10

        # Write the new hash value and wait number to the file
        with open(hash_file, "w") as f:
            f.write(f"{last_hash},{wait_number}")
    elif wait_number > 0:
        # The kernel.org update table has not been updated since the last check,
        # but we are still waiting before checking again.
        print(f"The kernel.org update table has not been updated since the last check. "
              f"Checking again for updates for {wait_number} time.")
        updating_gentoo_kernels()
        wait_number -= 1

        # Write the wait number to the file
        with open(hash_file, "w") as f:
            f.write(f"{last_hash},{wait_number}")
    else:
        # The kernel.org update table has not been updated since the last check,
        # and we have finished waiting. Reset the wait number and check again.
        print("The kernel.org update table has not been updated since the last check. "
              "Wait number=0.")
        last_hash = hash_value
        wait_number = 0

        # Write the new hash value and wait number to the file
        with open(hash_file, "w") as f:
            f.write(f"{last_hash},{wait_number}")
except Exception as e:
    print(f"Error occurred: {str(e)}")
finally:
    # Release the lock and close the file
    os.remove(lock_file)

# Remove the lock file if it still exists
if os.path.exists(lock_file):
    os.remove(lock_file)
