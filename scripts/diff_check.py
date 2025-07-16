#!/bin/env python
import os

CURRENT_DIR=os.path.dirname(os.path.realpath(__file__))
TEMPLATES_DIR=os.path.join(CURRENT_DIR+"/../templates/")
IRC_DIR=os.path.dirname(os.path.realpath(__file__))+"/../irc_bot/"
ROOT_DIR=CURRENT_DIR+"/../"+"gentoo_repository/sys-kernel/vanilla-sources/"
os.chdir(ROOT_DIR)

dir_list = os.listdir(ROOT_DIR)
print ("################# LONG")
for file in dir_list:
    if file not in ["metadata.xml", "Manifest"]:
        print ("------------------")
        print (file)
        os.system("diff -uNrp " + TEMPLATES_DIR + "vanilla-sources_loong.jinja "+ ROOT_DIR + "/" + file)
        print ("------------------")

print ("################# NOT LONG")
for file in dir_list:
    if file not in ["metadata.xml", "Manifest"]:
        print ("------------------")
        print (file)
        os.system("diff -uNrp " + TEMPLATES_DIR + "vanilla-sources.jinja "+ ROOT_DIR + "/" + file)
        print ("------------------")

