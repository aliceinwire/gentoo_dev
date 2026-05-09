#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

url = "https://raw.githubusercontent.com/graysky2/kernel_compiler_patch/master/more-uarches-for-kernel-5.17%2B.patch"
local_path = "/path/to/local/copy/more-uarches-for-kernel-5.17+.patch"

# fetch the content of the remote file
response = requests.get(url)
remote_content = response.content.decode("utf-8")

# read the content of the local file
with open(local_path, "r") as f:
    local_content = f.read()

# compare the content of the remote and local files
if remote_content == local_content:
    print("File is up-to-date!")
else:
    print("File has been updated!")
