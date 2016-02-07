#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Searches and extract updates for plugins

It uses uscan to search for updates currently you need to add
--download-current to the uscan command to intially get all plugins.
"""

import glob
import sh
import os, re, shutil
from debian import changelog

c = changelog.Changelog(open("debian/changelog").read())
UPSTREAM_VERSION = c.upstream_version

PLUGINS = []

def read():
    global PLUGINS
    with open("debian/plugins.overview") as f:
        c = f.read()

    p = c.split("\n\n")
    PLUGINS = []
    for i in p:
        l = re.finditer(r"(^|\n)(?P<key>[^:]+):(?P<value>([^\n]+|(\s*\n\s+[^\n]+)*))",i)
        PLUGINS.append(dict([(j.group("key").strip(),j.group("value").strip()) for j in l]))


def write():
    global PLUGINS
    with open("debian/plugins.overview", "w") as f:
        for p in PLUGINS:
            if (p != PLUGINS[0]):
                f.write("\n")
            f.write("\n".join(["%s: %s"%(k,p[k]) for k in ("Plugin", "Source", "Version")]))
            if p.get("Exclude-patterns"):
                f.write("\nExclude-patterns:\n %s"%(p["Exclude-patterns"]))
            f.write("\n")


def unpack(plugin):
    fname="../{pname}_{uversion}*.orig-{name}.tar*".format(pname=c.package, uversion=UPSTREAM_VERSION, name=plugin["Plugin"])
    fname = glob.glob(fname)[0]
    try:
        os.mkdir(plugin["Plugin"])
    except FileExistsError:
        shutil.rmtree(plugin["Plugin"])
        os.mkdir(plugin["Plugin"])
    sh.tar(["-C", plugin["Plugin"], "--strip-components=1", "-axf", fname])

def update(plugin):
    try:
        retcode = sh.uscan(["--watchfile", "debian/plugins/{Plugin}/watch".format(**plugin),
                            "--upstream-version", "{Version}".format(**plugin),
                            "--download", "--dehs"])
        newversion = re.search(r"<upstream-version>([\d.]+)</upstream-version>", str(retcode)).group(1)
        downloadurl = re.search(r"<upstream-url>(.+)</upstream-url>", str(retcode)).group(1)
        oldversion = plugin["Version"]
        plugin["Version"] = newversion
        plugin["Source"] = downloadurl
        print("New version found for {Plugin} ({oldversion}) -> ({Version}) {Source}".format(oldversion=oldversion, **plugin))
    except sh.ErrorReturnCode_1:
        pass

#read all plugins form overview
read()

#search for updates & download
for p in PLUGINS:
    update(p)

#write back
write()

#extract all plugins
for p in PLUGINS:
    unpack(p)
