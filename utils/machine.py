#!/usr/bin/env python
# Copyright (C) 2010-2015 Cuckoo Foundation.
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import argparse
import logging
import os.path
import sys

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".."))

from lib.cuckoo.common.config import Config
from lib.cuckoo.common.constants import CUCKOO_ROOT
from lib.cuckoo.core.database import Database

def get_conf(machinery, vmname, value):
    """Get info from a machine"""
    path = os.path.join(CUCKOO_ROOT, "conf", "%s.conf" % machinery)

    count = 0
    exist = False
    flag = False
    values = []

    file = open(path, "rb")
    for line in file:
	 line = line.strip()
         if line.split("=")[0].strip() == "machines":
	     machines = line.split("=", 1)[1].strip().replace(" ","").split(",")
	     for elem in machines:
		if elem == vmname:
		    exist = True
		    break
	     if exist == False:
	         print "The machine passed as argument does not exist in cuckoo"
	         exit(1)
	 if "[%s]" % vmname in line:
	    flag = True 
	    continue
	 if count < 4 and flag == True:	
	   v = line.split("=", 1)[1].strip()
	   values.append(v)
	   count = count + 1
 	   continue
	 elif count == 4:
	   break

    if value == "label":
	print values[0]
    elif value == "platform":
	print values[1]
    elif value == "ip":
	print values[2]
    elif value == "interface":
	print values[3]
    else:
	print "Invalid value"
	exit(1)

    exit(0)
		 
    

def delete_conf(machinery, vmname):
    """Delete a machine from the relevant configuration file"""
    path = os.path.join(CUCKOO_ROOT, "conf", "%s.conf" % machinery)
   
    flag = False
    count=0
    lines = []
    file = open(path, "rb")
    for line in file:
        line = line.strip()
        if line.split("=")[0].strip() == "machines":
            current_machines = []
	    machines = line.split("=", 1)[1].strip().replace(" ","").split(",")
     	    line = "machines ="
            for elem in machines:
		if elem != vmname:
		    current_machines.append(elem)
		    if line.split("=", 1)[1].strip():
		        line += ", %s" % current_machines[-1]
		    else:
			line += " %s" % current_machines[-1]
	if "[%s]" % vmname in line:
	    flag = True
            continue
        if count < 5 and flag == True:
            count = count + 1
	    continue
	lines.append(line)        

    open(path, "wb").write("\n".join(lines))


def update_conf(machinery, args, action=None):
    """Writes the new machine to the relevant configuration file."""
    path = os.path.join(CUCKOO_ROOT, "conf", "%s.conf" % machinery)

    lines = []
    for line in open(path, "rb"):
        line = line.strip()

        if line.split("=")[0].strip() == "machines":
             # If there are already one or more labels then append the new
             # label to the list, otherwise make a new list.
             if line.split("=", 1)[1].strip():
                 line += ", %s" % args.vmname
             else:
                 line += " %s" % args.vmname

        lines.append(line)

    if action == "add": 
        lines += [
            "",
            "[%s]" % args.vmname,
            "label = %s" % args.label,
            "platform = %s" % args.platform,
            "ip = %s" % args.ip,
        ]

    if args.snapshot:
        lines.append("snapshot = %s" % args.snapshot)

    if args.interface:
        lines.append("interface = %s" % args.interface)

    if args.resultserver:
        ip, port = args.resultserver.split(":")
        lines.append("resultserver_ip = %s" % ip)
        lines.append("resultserver_port = %s" % port)

    if args.tags:
        lines.append("tags = %s" % args.tags)

    open(path, "wb").write("\n".join(lines))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("vmname", type=str, help="Name of the Virtual Machine.")
    parser.add_argument("--debug", action="store_true", help="Debug log in case of errors.")
    parser.add_argument("--add", action="store_true", help="Add a Virtual Machine.")
    parser.add_argument("--delete", action="store_true", help="Delete a Virtual Machine")
    parser.add_argument("--get", type=str, help="Get info about a virtual machine")
    parser.add_argument("--ip", type=str, help="Static IP Address.")
    parser.add_argument("--platform", type=str, default="windows", help="Guest Operating System.")
    parser.add_argument("--tags", type=str, help="Tags for this Virtual Machine.")
    parser.add_argument("--interface", type=str, help="Sniffer interface for this machine.")
    parser.add_argument("--snapshot", type=str, help="Specific Virtual Machine Snapshot to use.")
    parser.add_argument("--resultserver", type=str, help="IP:Port of the Result Server.")
    parser.add_argument("--label", type=str, help="Label of the Virtual Machine")
    args = parser.parse_args()

    logging.basicConfig()
    log = logging.getLogger()

    if args.debug:
        log.setLevel(logging.DEBUG)

    db = Database()

    if args.resultserver:
        resultserver_ip, resultserver_port = args.resultserver.split(":")
    else:
        conf = Config()
        resultserver_ip = conf.resultserver.ip
        resultserver_port = conf.resultserver.port

    if args.add:
        db.add_machine(args.vmname, args.label, args.ip, args.platform,
                       args.tags, args.interface, args.snapshot,
                       resultserver_ip, int(resultserver_port))
        db.unlock_machine(args.vmname)

        update_conf(conf.cuckoo.machinery, args, action="add")

    if args.delete:
        # TODO Add a db.del_machine() function for runtime modification.
        update_conf(conf.cuckoo.machinery, args, action="delete")

    if args.delete:
        delete_conf(conf.cuckoo.machinery, args.vmname)	

    if args.get:
	get_conf(conf.cuckoo.machinery, args.vmname, args.get)


if __name__ == "__main__":
    main()
