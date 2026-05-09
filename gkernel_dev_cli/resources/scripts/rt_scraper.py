#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import shutil
import os
CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
IRC_DIR=os.path.dirname(os.path.realpath(__file__))+"/../irc_bot/"
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
ROOT_DIR=CURRENT_DIR+"/../"+"gentoo_repository/sys-kernel/rt-sources/"
print("change dir to rt-sources")
os.chdir(ROOT_DIR)


def get_links(branch):
    revision=0
    return_version=""
    versions=[]
    root_url='https://mirrors.edge.kernel.org/pub/linux/kernel/projects/rt/'
    r = requests.get(root_url + '/' + branch)
    soup = BeautifulSoup(r.content, 'html.parser')
    for link in soup.find_all('a',attrs={'href': re.compile("patches-"+branch+".*.\.tar\.gz")}):
        if 'rc' not in str(link):
            versions.append(link.get('href'))

    for version in versions:
        rt_revision=version.split("-")[2]
        rt_revision=rt_revision.split(".")[0].split('rt')[1]
        if int(rt_revision) > revision:
            revision = int(rt_revision)
            return_version=version
    return(return_version)
    
def rename_rt_packages(new_version,branch):
    exist_kernel_branch=True
    try:
        new_kernel_version=new_version.split('-')[1]
    except IndexError as err:
        exist_kernel_branch=False
        print(err)
        print("Not Released kernel branch: "+branch)
    if exist_kernel_branch:
        new_rt_version=new_version.split('-')[2].split(".")[0].split('rt')[1]
        # examplet: rt-sources-4.9.327_p197.ebuild
        new_rt_sources='rt-sources-'+new_kernel_version+"_p"+new_rt_version+".ebuild"
        # try to remove old version
        current_rt_sources_branch='rt-sources-'+branch
        old_rt_sources=None
        for path, currentDirectory, files in os.walk(ROOT_DIR):
            for file in files:
                if file.startswith(current_rt_sources_branch):
                    # check that new file and old file are differents
                    if new_rt_sources != file:
                        old_rt_sources=file
                        print("Found old file: "+old_rt_sources)

        # Remove old version
        if old_rt_sources:
            try:
                print("Removing: "+ old_rt_sources)
                os.remove(ROOT_DIR + old_rt_sources)
            except:
                print("not found file: " + old_rt_sources)

        # Add new version
        print("Adding: "+ new_rt_sources)
        if branch in old_branches: 
            shutil.copyfile(TEMPLATES_DIR+'/rt-sources_until_5.4.yaml',ROOT_DIR+new_rt_sources)
        else:
            shutil.copyfile(TEMPLATES_DIR+'/rt-sources.yaml',ROOT_DIR+new_rt_sources)



# inform channel that we are checking rt-sources
os.system('echo "checking rt-sources" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')

branches=['4.14','4.19','5.4','5.10','5.15','6.0','6.1','6.5','6.6','6.12']
# During the merging efforts the two Kconfig options were abandoned in the
# v5.4.3-rt1 release and since then there is only PREEMPT_RT which enables
# the full features set (as PREEMPT_RT_FULL did in earlier releases).
# https://github.com/torvalds/linux/commit/6829061315065c7af394d556a887fbf847e4e708
old_branches=['4.9','4.14','4.19','5.4']
# update gentoo repo
os.system("git pull --rebase=merges origin master -S")
for branch in branches:
    rename_rt_packages(get_links(branch),branch)
    os.system("pkgdev manifest")
    os.system("pkgdev commit -a")
