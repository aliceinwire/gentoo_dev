#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
import shutil

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from gkernel_dev_cli.lib.kernel_org import get_branches, get_links
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
ROOT_DIR=str(REPO_ROOT / "gentoo_repository" / "sys-kernel" / "vanilla-sources") + "/"
print("change dir to vanilla-sources")
os.chdir(ROOT_DIR)

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
    loong_kernels=["6.1","6.6","6.12","6.15","6.16","6.17"]
    if new_short_version in loong_kernels:
        shutil.copyfile(TEMPLATES_DIR+'vanilla-sources_loong.jinja',new_vanilla_sources)
    # remove previous one
    try:
        os.remove(ROOT_DIR + previous_vanilla_sources)
    except:
        print("not found dir: "+ROOT_DIR+previous_vanilla_sources)

os.chdir(ROOT_DIR)
branches=get_branches()
#branches=['6.17','6.16']
# Remove EOL branch
branches.remove('6.19')
## Add branch
## branches.append('6.19')
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
