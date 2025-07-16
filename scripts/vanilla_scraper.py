#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import os
import shutil

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
IRC_DIR=os.path.dirname(os.path.realpath(__file__))+"/../irc_bot/"
ROOT_DIR=CURRENT_DIR+"/../"+"gentoo_repository/sys-kernel/vanilla-sources/"
print("change dir to vanilla-sources")
os.chdir(ROOT_DIR)

# clean the html table and get the version number
def get_version_number(tr_html):
    # get list of td
    tr_html = tr_html.findChildren('td')
    # td 1 contains the kernel number
    tr_html = tr_html[1]
    # get the kernel number inside strong tag
    for node in tr_html.findAll('strong'):
        tr_html_number = ''.join(node.findAll(text=True))
    return tr_html_number


def find_new_version(version_number, argument_version):
    version = version_number.split('.', 2)
    # skip versions with no revisions
    # 6.2 (mainline) and use instead into 6.2.2 [stable]
    if int(len(version)) == 2:
        return None
    try:
        version = [version[0],version[1].split('-')[0]]
    except:
        pass
    try:
        version = version[0] + '.' + version[1]
        if version == argument_version:
            return version_number
        else:
            pass
    except:
        pass

def get_links(branch):
    revision=0
    return_version=""
    versions=[]
    root_url='https://kernel.org'
    r = requests.get(root_url)
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.findChildren('table')
    my_table = tables[2]
    tr_table = my_table.findChildren('tr')
    for i in tr_table:
        version_number = get_version_number(i)
        new_version_revision = find_new_version(version_number, branch)
        if new_version_revision is not None:
            break
    return(version_number)

def get_previous_version(new_version):
    new_revision=new_version.split('.')[2]
    minor=new_version.split('.')[1]
    major=new_version.split('.')[0]
    previous_revision=int(new_revision)-1
    previous_revision=str(previous_revision)
    previous_version=major+"."+minor+"."+previous_revision
    return previous_version
    
def rename_vanilla_packages(new_version):
    # clean revision if there is [EOL] tag
    if "EOL" in new_version:
        new_version=new_version.split(" ")[0]
    new_vanilla_sources='vanilla-sources-'+new_version+".ebuild"
    previous_version=(get_previous_version(new_version))
    previous_vanilla_sources='vanilla-sources-'+previous_version+".ebuild"
    print(previous_vanilla_sources)
    # check if already committed
    if os.path.exists(new_vanilla_sources):
        print("vanilla-sources already committed")
    else:
        print("committing vanilla sources")

    # add new vanilla-sources
    shutil.copyfile(TEMPLATES_DIR+'vanilla-sources.jinja',new_vanilla_sources)
    new_short_version=new_version.split(".")[0]+"."+new_version.split(".")[1]
    loong_kernels=["6.1","6.6","6.12","6.15","6.16"]
    if new_short_version in loong_kernels:
        shutil.copyfile(TEMPLATES_DIR+'vanilla-sources_loong.jinja',new_vanilla_sources)
    # remove previous one
    try:
        os.remove(ROOT_DIR + previous_vanilla_sources)
    except:
        print("not found dir: "+ROOT_DIR+previous_vanilla_sources)

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

# inform channel that we are checking vanilla-sources
#os.system('echo "checking vanilla-sources" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')
os.chdir(ROOT_DIR)
branches=get_branches()
# During the merging efforts the two Kconfig options were abandoned in the
# v5.4.3-rt1 release and since then there is only PREEMPT_RT which enables
# the full features set (as PREEMPT_RT_FULL did in earlier releases).
# https://github.com/torvalds/linux/commit/6829061315065c7af394d556a887fbf847e4e708
old_branches=['4.14','4.19','5.4']
# update gentoo repo
os.system("git pull --rebase=merges origin master -S")
for branch in branches:
    rename_vanilla_packages(get_links(branch))
    os.system("pkgdev manifest")
    os.system("pkgdev commit -a")
os.chdir(CURRENT_DIR)
