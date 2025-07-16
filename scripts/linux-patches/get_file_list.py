#!/usr/bin/env python
# -*- coding: utf-8 -*-

import jinja2
import os
import sys

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
GIT_DIR=os.path.dirname(os.path.realpath(__file__))+"/../..//git/"
SCRIPTS_DIR=os.path.dirname(os.path.realpath(__file__))+"/../../scripts/"
TEMPLATES_DIR=os.path.dirname(os.path.realpath(__file__))+"/../../templates/"
GENTOO_REPO_DIR=os.path.dirname(os.path.realpath(__file__))+"/../../gentoo_repository/"
LINUX_PATCHES_REPO_DIR=os.path.dirname(os.path.realpath(__file__))+"/../../linux-patches"
os.chdir(LINUX_PATCHES_REPO_DIR)
#print(LINUX_PATCHES_REPO_DIR)
# Get the list of all files and directories
path = "."
incr_patch_list=[]
added_patch_list=[]
dir_list = os.listdir(path)
for file in dir_list:
    if "_linux-" in file:
        incr_patch_list.append(file)
    else:
        if ".patch" in file:
            added_patch_list.append(file)

incr_patch_list.sort()
added_patch_list.sort()
#print("---------------------------")
#print(incr_patch_list)
#print("---------------------------")
#print(added_patch_list)
#print("---------------------------")
job_list=[]
# decide which interface to use based on the machine
templatedir = os.path.dirname(TEMPLATES_DIR)
templateLoader = jinja2.FileSystemLoader(searchpath=templatedir)
templateEnv = jinja2.Environment(loader=templateLoader)
template = templateEnv.get_template("/README_head.jinja")
jobdict = {}
jobt = template.render(jobdict)
job_list.append(jobt)

def get_kernel_version(patch):
    # 1000_linux-6.0.1.patch
    kernel_version = patch.split("-")[1].split(".patch")[0]
    #print(kernel_version)
    return kernel_version

for patch in incr_patch_list:
    kernel_version = get_kernel_version(patch)
    # decide which interface to use based on the machine
    templatedir = os.path.dirname(TEMPLATES_DIR)
    templateLoader = jinja2.FileSystemLoader(searchpath=templatedir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("/README_body.jinja")
    jobdict = {}
    jobdict["incr_patch_filename"] = patch
    jobdict["kernel_version"] = kernel_version
    jobt = template.render(jobdict)
    job_list.append(jobt)

## decide which interface to use based on the machine
#templatedir = os.path.dirname(os.path.abspath(__file__))
#templateLoader = jinja2.FileSystemLoader(searchpath=templatedir)
#templateEnv = jinja2.Environment(loader=templateLoader)
#template = templateEnv.get_template("templates/README_bottom.jinja")
#jobdict = {}
#jobt = template.render(jobdict)
#job_list.append(jobt)

def get_line_number(phrase, file_name):
    with open(file_name) as f:
        for i, line in enumerate(f, 1):
            if phrase in line:
                return i
        return i

# find first non incremental patch (the one not get from kernel.org incremental patches)
def find_first_ni_patch(file_name):
    with open(file_name) as f:
        for i, line in enumerate(f, 1):
            if "Patch: " in line:
                patch_name = line.split(" ")[2]
                patch_number = patch_name.split("_")[0]
                if int(patch_number) >= 1500:
                    return line

first_ni_patch = find_first_ni_patch(LINUX_PATCHES_REPO_DIR+"/0000_README")
first_ni_patch_ln = get_line_number(first_ni_patch, LINUX_PATCHES_REPO_DIR+"/0000_README")
EOF = get_line_number("EOF", LINUX_PATCHES_REPO_DIR+"/0000_README")

f = open("0000_README", "r")
Lines=f.readlines() #here you have a list of all the lines
new_text = []
for i in range((first_ni_patch_ln-1), EOF):
    new_text.append(Lines[i])

#for i in job_list:
#    print(i)
#for line in new_text:
#    print(line.strip("\n"))


with open('0000_README', 'w+') as f:
    for print_job in job_list:
        f.write('%s\n' %print_job)
    f.write('\n')
    for line in new_text:
        f.write(line)
f.close()
