#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import jinja2
import re
import os
import shutil
import sys

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
IRC_DIR=os.path.dirname(os.path.realpath(__file__))+"/../irc_bot/"
ROOT_DIR=CURRENT_DIR+"/../"+"gentoo_repository/sys-kernel/git-sources/"
print("change dir to git-sources")
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

def get_previous_git_version(new_version):
    if "rc" in new_version:
        new_revision=new_version.split('-')[1]
        new_version=new_version.split('rc')[1]
        previous_revision=int(new_version)-1
        previous_revision=str(previous_revision)
        previous_version="rc"+previous_revision
        return previous_version
    print("Not RC: "+new_version)
    sys.exit(0)

def get_base_branch(branch):
    major_version, minor_version = branch.split(".")
    minor_version = int(minor_version) - 1
    base_version = f"{major_version}.{minor_version}"
    return base_version

def template_write(base_branch):
    job_list=[]
    # decide which interface to use based on the machine
    templatedir = os.path.dirname(TEMPLATES_DIR)
    templateLoader = jinja2.FileSystemLoader(searchpath=templatedir)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template("/git-sources.jinja2")
    jobdict = {}
    jobdict["base_version"] = base_branch
    jobt = template.render(jobdict)
    job_list.append(jobt)
    return job_list

def create_new_version(new_git_sources, job_list):
    # add new git-sources
    with open(new_git_sources, 'w+') as f:
        for print_job in job_list:
            f.write('%s\n' %print_job)
        f.write('\n')
    f.close()
    
def rename_git_packages(new_version,branch):
    print("checking for RC version: "+ new_version)
    base_branch=get_base_branch(branch)
    print("K_BASE_VER="+base_branch)
    job_list=template_write(base_branch)
    # clean revision if there is [EOL] tag
    if "EOL" in new_version:
        new_version=new_version.split(" ")[0]
    new_git_sources="git-sources-"+new_version.replace("-","_")+".ebuild"
    # currently not removing old version
    #previous_version=(get_previous_git_version(new_version))
    #previous_git_sources='git-sources-'+branch+"_"+previous_version+".ebuild"

    # check if we commit new version
    if os.path.exists(new_git_sources):
        print("new git_sources already committed")
    else:
        print("not exist new git sources")
        create_new_version(new_git_sources, job_list)

        # inform channel that we are committing git-sources
        os.system('echo "commit git-sources version: ' + new_git_sources + '" >   '\
                  + IRC_DIR + '/irc.libera.chat/\#astat/in')

    #check if we remove previous version
    #if os.path.exists(previous_git_sources):
    #    print("exist previous")
    #else:
    #    print("not exist previous")
    # there is no 6.1 need to be removed
    #new_short_version=new_version.split(".")[0]+"."+new_version.split(".")[1]
    #if new_short_version == "6.1":
    #    shutil.copyfile(TEMPLATES_DIR+'git-sources_loong.jinja',new_git_sources)
    # remove previous one
    #try:
        #os.remove(ROOT_DIR + previous_git_sources)
    #except:
    #    print("not found dir: "+ROOT_DIR+previous_git_sources)

def get_mainline():
    # URL of the kernel.org page with the update table
    url = "https://www.kernel.org/"

    try:
        # Send an HTTP request to the website and get the response
        response = requests.get(url)

        # Use BeautifulSoup to parse the HTML content of the response
        soup = BeautifulSoup(response.content, "html.parser")

        # Find the table that lists the latest kernel versions
        table = soup.find("table", attrs={"id": "releases"})

        # Find the row that lists the latest mainline kernel version
        mainline_row = None
        for row in table.find_all("tr"):
            if "mainline:" in str(row):
                mainline_row = row
                break

        # Extract the mainline version number from the row
        mainline_version = None
        if mainline_row is not None:
            mainline_cells = mainline_row.find_all("td")
            if len(mainline_cells) >= 2:
                mainline_version = mainline_cells[1].text.strip()

        if mainline_version is not None:
            # Extract the major and minor version numbers from the mainline version
            match = re.match(r"(\d+\.\d+)", mainline_version)
            if match:
                major_minor_version = match.group(1)
                print(f"The latest mainline kernel version is {major_minor_version}.")
                return major_minor_version
            else:
                print("Unable to determine the latest mainline kernel version.")
        else:
            print("Unable to determine the latest mainline kernel version.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")



# inform channel that we are checking git-sources
os.system('echo "checking git-sources" >   ' + IRC_DIR + '/irc.libera.chat/\#astat/in')

branches=[get_mainline()]
# update gentoo repo
os.system("git pull --rebase=merges origin master -S")
for branch in branches:
    print(branch)
    rename_git_packages(get_links(branch),branch)
    os.system("pkgdev manifest")
    os.system("pkgdev commit -a")
