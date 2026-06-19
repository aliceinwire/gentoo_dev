#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import sys
from pathlib import Path
import subprocess
import jinja2

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from gkernel_dev_cli.lib.kernel_org import get_branches, get_links
LINUX_PATCHES_REPO_DIR=str(REPO_ROOT / "linux-patches") + "/"
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
ROOT_DIR=str(REPO_ROOT / "gentoo_repository" / "sys-kernel" / "gentoo-sources") + "/"

def _parse_gentoo_sources_filename(branch, filename):
    pattern = re.compile(
        rf"^gentoo-sources-{re.escape(branch)}\.(?P<patch>\d+)(?:-r(?P<revision>\d+))?\.ebuild$"
    )
    match = pattern.match(filename)
    if not match:
        return None
    return {
        "filename": filename,
        "patch": int(match.group("patch")),
        "revision": int(match.group("revision") or 0),
        "version": match.group("patch")
        + (f"-r{match.group('revision')}" if match.group("revision") else ""),
    }

def _get_kernel_org_patch(branch):
    latest_version = get_links(branch)
    if latest_version is None:
        raise ValueError(f"No kernel.org release found for branch {branch}")
    if latest_version == branch:
        return 0
    branch_prefix = f"{branch}."
    if not latest_version.startswith(branch_prefix):
        raise ValueError(
            f"kernel.org release {latest_version} does not match branch {branch}"
        )
    patch = latest_version[len(branch_prefix):].split("-", 1)[0]
    try:
        return int(patch)
    except ValueError as exc:
        raise ValueError(
            f"Unable to parse patch version from kernel.org release {latest_version}"
        ) from exc


def _is_available_on_kernel_org(branch, patch):
    kernel_org_patch = _get_kernel_org_patch(branch)
    if patch <= kernel_org_patch:
        return True
    print(
        f"Skipping gentoo-sources-{branch}.{patch}.ebuild: "
        f"latest kernel.org release for {branch} is {branch}.{kernel_org_patch}"
    )
    return False

def _get_gentoo_sources_versions(branch):
    dir_files = os.listdir(ROOT_DIR)
    versions = [
        parsed
        for file in dir_files
        if (parsed := _parse_gentoo_sources_filename(branch, file)) is not None
    ]
    return sorted(versions, key=lambda version: (version["patch"], version["revision"]))

def get_latest_tag(branch):
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
    target="gentoo-sources-" + branch
    print("target: " + target)
    return [version["version"] for version in _get_gentoo_sources_versions(branch)]

def get_latest_gentoo_sources_ebuild(branch):
    version_list = _get_gentoo_sources_versions(branch)
    if not version_list:
        raise FileNotFoundError(f"No gentoo-sources ebuilds found for branch {branch}")
    return version_list[-1]

def get_committed_tag(branch):
    os.chdir(ROOT_DIR)
    version_list = get_version_list(branch)
    gs_last_version=str(max(version_list))
    gentoo_sources_last=get_latest_gentoo_sources_ebuild(branch)["filename"]
    print("gs_last:"+str(gentoo_sources_last))
    with open(gentoo_sources_last, 'r') as gentoo_sources_ebuild:
        ebuild_lines = gentoo_sources_ebuild.readlines()
        for row in ebuild_lines:
            word = 'K_GENPATCHES_VER='
            if row.find(word) != -1:
                k_genpatches_ver=row.split('=')[1].replace('"','').strip()
                break
        else:
            raise ValueError(f"K_GENPATCHES_VER not found in {gentoo_sources_last}")

    return k_genpatches_ver

def create_filename(branch):
    latest_ebuild = get_latest_gentoo_sources_ebuild(branch)
    gentoo_sources_new_version=latest_ebuild["patch"]+1
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

def main():
    branches=get_branches()
    print(branches)
    #branches=["6.19","6.18",'6.12','6.6','6.1','5.15','5.10']
    #branches=['6.17','6.16']
    # Remove EOL branch
    ##branches.remove('6.19')
    ## Add branch
    ## branches.append('6.19')
    # update gentoo repo
    os.chdir(ROOT_DIR)
    os.system("git pull --rebase=merges origin master -S")
    for branch in branches:
        print("start work in :"+branch)
        last_tag=get_latest_tag(branch)
        print(last_tag)
        current_k_genpatches_version=get_committed_tag(branch)
        print("latest tag="+last_tag+" k_genpatches_version="+current_k_genpatches_version)
        if int(last_tag) != int(current_k_genpatches_version):
            print("latest tag="+last_tag+" is different from last k_genpatches_version="+current_k_genpatches_version)
            new_filename=create_filename(branch)
            latest_ebuild = get_latest_gentoo_sources_ebuild(branch)
            new_patch = latest_ebuild["patch"] + 1
            if not _is_available_on_kernel_org(branch, new_patch):
                continue
            new_gentoo_sources=create_new_gentoo_sources(last_tag,branch)
            #print(new_gentoo_sources)
            print(new_filename)
            with open(new_filename, "w") as gs:
                gs.write(new_gentoo_sources)
            os.system("pkgdev manifest --distdir=/var/cache/distfiles/")
            os.system("ebuild " + new_filename + " clean test install")
            os.system("ebuild " + new_filename + " clean")
            os.system("pkgdev commit -a")
    os.chdir(CURRENT_DIR)

if __name__ == "__main__":
    main()
