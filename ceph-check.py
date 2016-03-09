#!/usr/bin/env python

from __future__ import print_function
import time
import subprocess
import sys
import os
import json
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
        print("\nRunning ceph-check :-\n")
        print("Conditions for successfully executing this program:-")
        print("1. This program should be executed from the Ceph Admin node.")
        print(
            "2. This should be executed as the 'ceph' user, or as the user as which 'ceph-deploy' was run.")
        print(
            "3. The user executing this program should have 'read' permissions to the Ceph client Admin keyring.\n")
        self.keyring_check()

    def keyring_check(self):
        """Check if a custom keyring exists
        :rtype: basestring
        """
        config_file = ConfigParser.SafeConfigParser()
        config_file.read(CONFFILE)
        try:
            print("Checking for custom admin keyring path in", CONFFILE)
            keyring_custom = config_file.get('global', 'keyring')
            print("Admin keyring found at", keyring_custom)
            self.keyring_permission(keyring_custom)
        except ConfigParser.NoOptionError:
            print("No custom keyring found, falling back to", KEYRING)
            self.keyring_permission(KEYRING)

    def keyring_permission(self, keyring_custom):
        if os.access(keyring_custom, os.R_OK):
            self.ceph_report()
        else:
            print(
                os.getlogin(), "does not have read permissions for", keyring_custom)
            print("Exiting!\n")
            sys.exit()

    def ceph_report(self):
        report = "/tmp/ceph-report-" + time.strftime("%d%m%Y-%H%M%S")
        try:
            with open(report, "w") as output:
                print("\nRunning 'ceph report' and saving to", report, '\n')
                subprocess.call(["/usr/bin/ceph", "report"], stdout=output)
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
        with open(report) as obj:
            print("\nParsing ceph report - Remove this line\n")
            json_obj = json.load(obj)
            print("Cluster status :-", json_obj['health']['overall_status'])

    def ssh_check(self):
        """Check the ssh access to the MON/OSD nodes, and print
            a) Hostname
            b) IP address
            c) ....
        """
        pass

if __name__ == "__main__":
    checker = CephCheck(CONFFILE, KEYRING)
    # Testing conf and keyring paths.
    # print(checker.conf)
    # print(checker.keyring)
    checker.notify()
