from __future__ import annotations

import requests
from bs4 import BeautifulSoup


ROOT_URL = "https://kernel.org"


def get_version_number(tr_html):
    tr_html = tr_html.findChildren("td")
    tr_html = tr_html[1]
    for node in tr_html.findAll("strong"):
        tr_html_number = "".join(node.findAll(text=True))
    return tr_html_number


def find_new_version(version_number, argument_version):
    version = version_number.split(".", 2)
    if int(len(version)) == 2:
        return None
    try:
        version = [version[0], version[1].split("-")[0]]
    except Exception:
        pass
    try:
        version = version[0] + "." + version[1]
        if version == argument_version:
            return version_number
    except Exception:
        pass
    return None


def get_links(branch):
    r = requests.get(ROOT_URL)
    soup = BeautifulSoup(r.content, "lxml")
    tables = soup.findChildren("table")
    my_table = tables[2]
    tr_table = my_table.findChildren("tr")
    for i in tr_table:
        version_number = get_version_number(i)
        new_version_revision = find_new_version(version_number, branch)
        if new_version_revision is not None:
            break
    return version_number


def get_kernel(tr_html):
    tr_html = tr_html.findChildren("td")
    version_html = tr_html[1]
    branch_html = tr_html[0]
    for node in version_html.findAll("strong"):
        version_string = "".join(node.findAll(text=True))
    branch_string = "".join(branch_html.findAll(text=True))
    return branch_string + " " + version_string


def get_branches():
    branches = []
    kernel_string = []
    r = requests.get(ROOT_URL)
    soup = BeautifulSoup(r.content, "lxml")
    tables = soup.findChildren("table")
    my_table = tables[2]
    tr_table = my_table.findChildren("tr")
    for i in tr_table:
        kernel_string.append(get_kernel(i))
    for i in kernel_string:
        kernel_release = i.split(" ")[0]
        if kernel_release in {"stable:", "longterm:"}:
            parts = i.split(" ")[1].split(".")
            branches.append(parts[0] + "." + parts[1])
    return branches

