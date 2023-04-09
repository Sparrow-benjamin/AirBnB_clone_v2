#!/usr/bin/python3
"""
Distributes archived pack to both web servers
Usage:
    fab -f 2-do_deploy_web_static.py do_deploy:archive_path=versions/<file_name> -i my_ssh_private_key
"""

from os import path
from fabric.api import *

env.user = "ubuntu"
env.hosts = ["34.139.131.161", "44.200.101.61"]


def do_deploy(archive_path):
    """
    Distributes an archive to a web server.
    return false if unsuccessfull
    """
    if path.isfile(archive_path) is False:
        return False
    file_tgz = archive_path.split("/")[-1]
    folder = fullFile.split(".")[0]

    # uploads archive to /tmp/ directory
    if put(archive_path, "/tmp/{}".format(file_tgz)).failed is True:
        return False

    # delete the archive folder on the server
    if run("rm -rf /data/web_static/releases/{}/".
           format(folder)).failed is True:
        return False

    # create a new archive folder
    if run("mkdir -p /data/web_static/releases/{}/".
           format(folder)).failed is True:
        return False

    # uncompress archive to /data/web_static/current/ directory
    if run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".
           format(file_tgz, folder)).failed is True:
        return False

    if run("sudo rm /tmp/{}".format(fullFile)).failed is True:
        return False

     # delete current folder being served (the symbolic link)
    if run("rm -rf /data/web_static/current").failed is True:
        return False


     # move folder from web_static to its parent follder
    if run("mv /data/web_static/releases/{}/web_static/* "
           "/data/web_static/releases/{}/".
           format(folder, folder)).failed is True:
        return False

    # delete the empty web_static file, as its content have been moved to
    # its parent directory
    if run("rm -rf /data/web_static/releases/{}/web_static".
           format(folder)).failed is True:
        return False


    # create new symbolic link on web server linked to new code version
    if run("ln -s /data/web_static/releases/{}/ /data/web_static/current".
           format(folder)).failed is True:
        return False

    print("New version deployed!")
    return True
