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

# __author__ = "Vimal A.R"
# __version__ = "v0.1"
# __license__ = "GNU GPL v2.0"
# __email__ = "vimal@redhat.com"

from __future__ import print_function
import time
import subprocess
import sys
import os
import json
import getpass
import ConfigParser
import logging

CONF_FILE = "/etc/ceph/ceph.conf"
ADMIN_KEYRING = "/etc/ceph/ceph.client.admin.keyring"
CEPH_CHECK_LOG = os.path.expanduser("~") + "/ceph_check.log"

# LOGGING MODULE CONFIG ###
# 1. Set the application name (override the default `root` user)
cc_logger = logging.getLogger("ceph_check:")
cc_logger.setLevel(logging.INFO)
# 2. Set a Log handler
handler = logging.FileHandler(CEPH_CHECK_LOG)
# 3. Set up a log format
log_format = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')
# 4. Pass the log format to the log handler
handler.setFormatter(log_format)
# 5. Add the log handler to the logger object `cc_logger`
cc_logger.addHandler(handler)
# LOGGING MODULE CONFIG END ###


class CephCheck(object):
    """The main ceph-check class"""

    def __init__(self, conffile, keyring):
        self.conffile = conffile
        self.keyring = keyring
        self.help()

    def notify(self):
        cc_logger.info("Starting ceph_check")
        print("## Starting ceph_check\n")
        self.keyring_check()

    def keyring_check(self):
        """
        Check if a custom keyring exists
        """
        config_file = ConfigParser.SafeConfigParser()
        cc_logger.info("Reading %s" % CONF_FILE)
        config_file.read(self.conffile)
        cc_logger.info("Checking keyring")
        try:
            keyring_custom = config_file.get('global', 'keyring')
            cc_logger.info("Found %s" % self.keyring_custom)
            self.keyring_permission(keyring_custom)
        except ConfigParser.NoOptionError:
            cc_logger.info("No custom admin keyring specified in %s" % self.conffile)
            cc_logger.info("Falling back to %s" % self.keyring)
            cc_logger.info("Calling keyring_permission()")
            self.keyring_permission(self.keyring)

    def keyring_permission(self, keyring):
        """
        Check the existence and permission of the keyring
        """
        if os.path.isfile(self.keyring):
            cc_logger.info("%s exits" % self.keyring)
            if os.access(self.keyring, os.R_OK):
                cc_logger.info("%s has read permissions" % self.keyring)
                cc_logger.info("Calling ceph_report()")
                self.ceph_report()
            else:
                cc_logger.info("User %s does not have read permissions \
                    for %s" % getpass.getuser, self.keyring)
                print("\nERROR: User", getpass.getuser(),
                      "does not have read permissions for", self.keyring)
                cc_logger.info("Exiting!")
                print("\nExiting!\n")
                sys.exit(-1)
        else:
            cc_logger.info("Cannot find keyring at %s" % keyring)
            print("\nCannot find keyring at", keyring)
            cc_logger.info("Exiting!")
            print("\nExiting!\n")
            sys.exit()

    def ceph_report(self):
        report = "/tmp/report-" + time.strftime("%d%m%Y-%H%M%S")
        cc_logger.info("Generating cluster report")
        try:
            with open(report, "w") as output:
                subprocess.call(["/usr/bin/ceph", "report"], stdout=output, )
                cc_logger.info("Saved to %s" % report)
                cc_logger.info("Calling report_parse_summary()")
                self.report_parse_summary(report)

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
    checker = CephCheck(CONF_FILE, ADMIN_KEYRING)
    checker.notify()
