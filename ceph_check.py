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
    checker = CephCheck(CONFFILE, KEYRING)
    checker.notify()
