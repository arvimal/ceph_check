#!/usr/bin/env python

from __future__ import print_function
import time
import subprocess
import sys
import os
import json
import getpass
import ConfigParser


__author__ = "Vimal A.R"
__version__ = "v0.1"
__license__ = "GNU GPL v2.0"
__email__ = "vimal@redhat.com"

CONFFILE = "/etc/ceph/ceph.conf"
KEYRING = "/etc/ceph/ceph.client.admin.keyring"


class CephCheck(object):
    """The main ceph-check class"""

    def __init__(self, conffile, keyring):
        self.conf = conffile
        self.keyring = keyring

    def notify(self):
        print("\nRunning ceph_check :-\n")
        print("Conditions for successfully executing this program:-")
        print("* This program should be executed from the Ceph Admin node.")
        print("* This should be executed as the 'ceph' user, or as the user as which 'ceph-deploy' was run.")
        print("* The user should have read permissions to the Ceph client Admin keyring.\n")
        self.keyring_check()

    def keyring_check(self):
        """
        Check if a custom keyring exists
        """
        config_file = ConfigParser.SafeConfigParser()
        config_file.read(CONFFILE)
        print("1. Admin keyring\n")
        try:
            print("Checking if a custom admin keyring is present.")
            keyring_custom = config_file.get('global', 'keyring')
            print(CONFFILE, "lists admin keyring at", keyring_custom)
            self.keyring_permission(keyring_custom)
        except ConfigParser.NoOptionError:
            print("No custom keyring found")
            print("Falling back to", KEYRING)
            self.keyring_permission(KEYRING)

    def keyring_permission(self, keyring_custom):
        """
        Check the existence and permission of the keyring
        """
        if os.path.isfile(keyring_custom):
            if os.access(keyring_custom, os.R_OK):
                self.ceph_report()
            else:
                print("\nERROR: User", getpass.getuser(), "does not have read permissions for", keyring_custom)
                print("\nExiting!\n")
                sys.exit()
        else:
            print("\nCannot find keyring at", keyring_custom)
            print("\nExiting!\n")
            sys.exit()

    def ceph_report(self):
        report = "/tmp/report-" + time.strftime("%d%m%Y-%H%M%S")
        print("\n2. Cluster report\n")
        try:
            with open(report, "w") as output:
                print("Generating cluster status report")
                subprocess.call(["/usr/bin/ceph", "report"], stdout=output)
                print("Saved to", report)
                self.report_parse(report)
        except IOError:
            # It's very unlikely we'll hit this and exit here.
            print("\nCannot create", report)
            print("Check permissions, exiting!\n")
            sys.exit()

    def report_parse(self, report):
        """Gets the MON/OSD node list for now
            Can add more parsers later
        """
        print("\n3. Analyzing the report")
        with open(report) as obj:
            json_obj = json.load(obj)
            cluster_status = json_obj['health']['overall_status']
            print("\nCluster status : ", cluster_status,"\n")
            if cluster_status != "HEALTH_OK":
                # We iterate over each object within the "summary" dict,
                # and print the 'value' for the 'summary' key
                print("\t*Summary: ")
                for i in json_obj['health']['summary']:
                    print(i['summary'])
        self.mon_status_check(report)
        self.osd_status_check(report)

    def mon_status_check(self, report):
        print("\n\t* MON status: ")

    def osd_status_check(self, report):
        print("\n\t* OSD status: ")

    def pool_info(self, report):
        print("\n\t* Pool status")

    def pg_info(self, report):
        print("\n\t* Placement Group status")

    def ssh_check(self):
        """Check the ssh access to the MON/OSD nodes, and print
            a) Hostname
            b) IP address
            c) ....
        """
        pass

if __name__ == "__main__":
    checker = CephCheck(CONFFILE, KEYRING)
    checker.notify()
