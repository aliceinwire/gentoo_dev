#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import requests
import hashlib
from bs4 import BeautifulSoup

# URL of the file server
url = "https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/"

# Directories to check for changes
dirs = ["6.2", "6.1"]

# Path of the file to store the previous hash
hash_file_path = "/tmp/rt_fileserver_hash.txt"

# Load the previous hash from the file, if it exists
if os.path.exists(hash_file_path):
    with open(hash_file_path, "r") as f:
        previous_links_hash = f.read().strip()
else:
    previous_links_hash = ""

# Function to recursively search for files
def search_for_files(path):
    global previous_links_hash

    # Load the page content
    response = requests.get(path)
    content = response.content

    # Parse the page content with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    # Get all the file links on the page
    links = soup.find_all("a")

    # Create a list of file links
    file_links = []
    for link in links:
        href = link.get("href")
        if href.endswith(".tar.bz2") or href.endswith(".patch"):
            file_links.append(href)

    print(file_links)
    # Calculate the hash of the file links
    current_links_hash = hashlib.sha256("".join(file_links).encode()).hexdigest()

    # Compare the hashes to check for changes
    if current_links_hash != previous_links_hash:
        print("There are updates on the file server!")
        print("New file links in", path + ":")
        for link in file_links:
            print(link)

        # Update the hash of the file links
        previous_links_hash = current_links_hash

        # Save the new hash to the file
        with open(hash_file_path, "w") as f:
            f.write(previous_links_hash)

    # Recursively search for files in subdirectories
    for link in links:
        href = link.get("href")
        if href.endswith("/") and href[:-1] in dirs:
            search_for_files(path + href)

# Start the search in the root directory
search_for_files(url)
