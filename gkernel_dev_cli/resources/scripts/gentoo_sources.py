#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import os
import sys
from pathlib import Path
import shutil
import subprocess
import jinja2

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = Path(__file__).resolve().parents[3]
LINUX_PATCHES_REPO_DIR=os.path.dirname(os.path.realpath(__file__))+"/../linux-patches/"
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
ROOT_DIR=str(REPO_ROOT / "gentoo_repository" / "sys-kernel" / "gentoo-sources") + "/"

def get_latest_tag():
    # get in linux patches
    os.chdir(LINUX_PATCHES_REPO_DIR)
    # chaange to branch
    os.system("git checkout "+branch)
    # get latest tag
    last_tag=subprocess.getoutput("git describe --abbrev=0 --tags")
    last_tag=last_tag.split('-')[1]
    return last_tag

def get_version_list(branch):
    # get in gentoo-sources
    os.chdir(ROOT_DIR)
    #os.system("ls *"+branch+"*")
    gentoo_sources_last=""
    dir_files=os.listdir(ROOT_DIR)
    dir_files = sorted(dir_files)
    target="gentoo-sources-" + branch
    print("target: " + target)
    prefix = f"{target}."
    version_list = [file.removeprefix(prefix) for file in dir_files if file.startswith(prefix)]
    version_list = [file.removesuffix(".ebuild") for file in version_list]
    return version_list


def get_committed_tag(branch):
    os.chdir(ROOT_DIR)
    version_list = get_version_list(branch)
    gs_last_version=str(max(version_list))
    gentoo_sources_last="gentoo-sources-"+branch+"."+gs_last_version+".ebuild"
    print("gs_last:"+str(gentoo_sources_last))
    with open(gentoo_sources_last, 'r') as gentoo_sources_ebuild:
        ebuild_lines = gentoo_sources_ebuild.readlines()
        for row in ebuild_lines:
            word = 'K_GENPATCHES_VER='
            if row.find(word) != -1:
                k_genpatches_ver=row.split('=')[1].replace('"','')
    return k_genpatches_ver

def create_filename(branch):
    gentoo_sources_last=""
    version_list = get_version_list(branch)
    gs_last_version=str(max(version_list))
    gentoo_sources_last="gentoo-sources-"+branch+"."+gs_last_version+".ebuild"
    gentoo_sources_version=gentoo_sources_last.split("-")[2].split(".")[2]
    gentoo_sources_new_version=int(gentoo_sources_version)+1
    # gentoo-sources-5.15.93.ebuild
    new_filename="gentoo-sources-"+branch+"."+str(gentoo_sources_new_version)+".ebuild"
    return new_filename


def create_new_gentoo_sources(version,branch):
    job_list=[]
    # decide which interface to use based on the machine
    templatedir = os.path.dirname(TEMPLATES_DIR)
    templateLoader = jinja2.FileSystemLoader(searchpath=templatedir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    loong_kernels=["6.12","6.15","6.16","6.17"]
    if branch in loong_kernels:
        template = templateEnv.get_template("/gentoo-sources_loong.jinja2")
    elif branch == "6.6":
        template = templateEnv.get_template("/gentoo-sources_6_6.jinja2")
    elif branch == "5.15":
        template = templateEnv.get_template("/gentoo-sources_5_15.jinja2")
    else:
        template = templateEnv.get_template("/gentoo-sources.jinja2")
    jobdict = {}
    jobdict["k_genpatches_ver"] = version
    jobt = template.render(jobdict)
    job_list.append(jobt)
    return jobt

# clean the html table and get the version number
def get_kernel(tr_html):
    # get list of td
    tr_html = tr_html.findChildren('td')
    # td 1 contains the kernel number
    version_html = tr_html[1]
    branch_html = tr_html[0]
    # get the kernel number inside strong tag
    for node in version_html.findAll('strong'):
        version_string = ''.join(node.findAll(text=True))
    branch_string=''.join(branch_html.findAll(text=True))
    return branch_string + " " + version_string

def get_branches():
    branches=[]
    kernel_string=[]
    root_url='https://kernel.org'
    r = requests.get(root_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.findChildren('table')
    my_table = tables[2]
    tr_table = my_table.findChildren('tr')
    for i in tr_table:
        kernel_string.append(get_kernel(i))
    for i in kernel_string:
        kernel_release=i.split(" ")[0]
        if kernel_release == "stable:" or kernel_release == "longterm:":
            branches.append(i.split(" ")[1].split(".")[0]+"."+i.split(" ")[1].split(".")[1])
    return(branches)

#branches=get_branches()
branches=["6.19","6.18",'6.12','6.6','6.1','5.15','5.10']
# update gentoo repo
os.chdir(ROOT_DIR)
os.system("git pull --rebase=merges origin master -S")
for branch in branches:
    print("start work in :"+branch)
    last_tag=get_latest_tag()
    print(last_tag)
    current_k_genpatches_version=get_committed_tag(branch)
    print("latest tag="+last_tag+" k_genpatches_version="+current_k_genpatches_version)
    if int(last_tag) != int(current_k_genpatches_version):
        print("latest tag="+last_tag+" is different from last k_genpatches_version="+current_k_genpatches_version)
        new_gentoo_sources=create_new_gentoo_sources(last_tag,branch)
        #print(new_gentoo_sources)
        new_filename=create_filename(branch)
        print(new_filename)
        with open(new_filename, "w") as gs:
            gs.write(new_gentoo_sources)
        os.system("pkgdev manifest --distdir=/var/cache/distfiles/")
        os.system("pkgdev commit -a")
os.chdir(CURRENT_DIR)
