#!/usr/bin/env python

# Copyright (C) 2010 Red Hat, Inc., Vimal A.R <vimal@redhat.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


from __future__ import print_function
import time
import subprocess
import sys
import os
import json
import getpass
import ConfigParser
import logging

__author__ = "Vimal A.R"
__version__ = "v0.1"
__license__ = "GNU GPL v2.0"
__email__ = "vimal@redhat.com"

CONFFILE = "/etc/ceph/ceph.conf"
ADMIN_KEYRING = "/etc/ceph/ceph.client.admin.keyring"


class CephCheck(object):
    """The main ceph-check class"""

    def __init__(self, conffile, keyring):
        self.conf = conffile
        self.keyring = keyring
        self.help()

    def notify(self):
        print("## Running ceph_check\n")
        self.keyring_check()

    def keyring_check(self):
        """
        Check if a custom keyring exists
        """
        config_file = ConfigParser.SafeConfigParser()
        config_file.read(self.conf)
        print("## Checking keyring -\n")
        try:
            print("-Checking for a custom admin keyring.")
            keyring_custom = config_file.get('global', 'keyring')
            print(self.keyring, "lists admin keyring at", keyring_custom)
            self.keyring_permission(keyring_custom)
        except ConfigParser.NoOptionError:
            print("-No custom keyring found")
            print("-Falling back to", self.keyring)
            self.keyring_permission(self.keyring)

    def keyring_permission(self, keyring):
        """
        Check the existence and permission of the keyring
        """
        if os.path.isfile(self.keyring):
            if os.access(self.keyring, os.R_OK):
                self.ceph_report()
            else:
                print("\nERROR: User", getpass.getuser(),
                      "does not have read permissions for", self.keyring)
                print("\nExiting!\n")
                sys.exit()
        else:
            print("\nCannot find keyring at", keyring)
            print("\nExiting!\n")
            sys.exit()

    def ceph_report(self):
        report = "/tmp/report-" + time.strftime("%d%m%Y-%H%M%S")
        print("\n## Generating cluster report -\n")
        try:
            with open(report, "w") as output:
                subprocess.call(["/usr/bin/ceph", "report"], stdout=output)
                print("Saved to", report)
                self.report_parse_summary(report)
        # Write an exception handler for a timeout error, example:
        # $ ceph report
        # 2016-07-14 20:06:53.996526 7efdc365b700  0 monclient(hunting): authenticate timed out after 300
        # 2016-07-14 20:06:53.996559 7efdc365b700  0 librados: client.admin authentication error (110) Connection timed out
        # Error connecting to cluster: TimedOut

        except IOError:
            # It's very unlikely we'll hit this and exit here.
            print("\nCannot create", report)
            print("Check permissions, exiting!\n")
            sys.exit()

    def report_parse_summary(self, report):
        """Gets the MON/OSD node list for now
            Can add more parsers later
        """
        print("\n## Analysing the cluster report -")
        with open(report) as obj:
            json_obj = json.load(obj)
            cluster_status = json_obj['health']['overall_status']
            print("\n#Cluster status : ", cluster_status, "\n")
            # Get this printed in RED color :)
            if cluster_status != "HEALTH_OK":
                # Print a general cluster summary
                # We iterate over each object within the "summary" dict,
                # and print the 'value' for the 'summary' key
                print("#Cluster summary:\n")
                for i in json_obj['health']['summary']:
                    print(i['summary'])
        self.cluster_status(report)

    def cluster_status(self, report):
        # Calling all helper functions irrespective of cluster status
        self.mon_status_check(report)
        self.osd_status_check(report)
        self.pool_info(report)
        self.pg_info(report)
        # Calling the generic system config checks
        self.ssh_check()

    def get_osd_and_mon(report):
        """Get the list of MONs and OSDs from the report"""
        pass
        # Note for self: Refer ceph_osd_meta.py from ceph report parse

    # 1. Cluster checks (MON, OSD, PG, Pool etc..)

    def mon_status_check(self, report):
        print("\n# MON status: \n")
        with open(report) as obj:
            json_obj = json.load(obj)
            print("Mon map epoch: %s\n" % str(json_obj['monmap']['epoch']))
            for mon in json_obj['monmap']['mons']:
                print("Monitor rank : %s" % str(mon['rank']))
                print("Host name    : %s" % str(mon['name']))
                print("IP Address   : %s\n" % str(mon['addr']))
                print("Port         : %s\n" % str(mon['addr']).strip([":"]))

    def osd_status_check(self, report):
        print("\n# OSD status: \n")

    def pool_info(self, report):
        print("\n# Pool status: \n")

    def pg_info(self, report):
        print("\n# Placement Group status: \n")

    # 2. System config checks (SSH access, hardware, RAID etc.. )
    def ssh_check(self):
        """Check the ssh access to the MON/OSD nodes, and print
            a) Hostname
            b) IP address
            c) ....
        """
        print("Checking SSH passwordless access to the Cluster nodes")
        print("Get a dict of hostname and IP address of MONs and OSD nodes")
        pass

    def help(self):
        print("\n## Conditions for successfully executing this program:-\n")
        print("-Best run from the Admin node, as the user assigned to run `ceph-deploy`.")
        print("-The user should have read permissions to the Admin keyring.\n")


if __name__ == "__main__":
    checker = CephCheck(CONFFILE, KEYRING)
    checker.notify()
