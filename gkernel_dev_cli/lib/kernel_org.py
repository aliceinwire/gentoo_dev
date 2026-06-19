from __future__ import annotations

import requests
from bs4 import BeautifulSoup


ROOT_URL = "https://kernel.org"
KERNEL_RELEASE_TYPES = {"mainline:", "stable:", "longterm:"}


def _get_release_rows(soup):
    rows = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) < 2:
                continue
            release_type = columns[0].get_text(" ", strip=True)
            if release_type in KERNEL_RELEASE_TYPES:
                rows.append(row)
    return rows


def get_version_number(tr_html):
    tr_html = tr_html.find_all("td")
    tr_html = tr_html[1]
    version = tr_html.find("strong")
    if version is None:
        return tr_html.get_text(" ", strip=True).split(" ")[0]
    return version.get_text("", strip=True)



def find_new_version(version_number, argument_version):
    version = version_number.split(".", 2)
    if len(version) == 2:
        if version_number == argument_version:
            return version_number
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
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "lxml")
    for i in _get_release_rows(soup):
        version_number = get_version_number(i)
        new_version_revision = find_new_version(version_number, branch)
        if new_version_revision is not None:
            return new_version_revision
    return None


def get_kernel(tr_html):
    columns = tr_html.find_all("td")
    branch_html = columns[0]
    version_string = get_version_number(tr_html)
    branch_string = branch_html.get_text("", strip=True)
    return branch_string + " " + version_string


def get_branches():
    branches = []
    r = requests.get(ROOT_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "lxml")
    for i in _get_release_rows(soup):
        release_type, version = get_kernel(i).split(" ", 1)
        if release_type in KERNEL_RELEASE_TYPES:
            parts = version.split(".")
            branches.append(parts[0] + "." + parts[1])
    return branches
