#!/usr/bin/env python

from __future__ import print_function
import time
import subprocess
import json
import sys
import os
import getpass
import ConfigParser
import logging
import logging.handlers

CONF_FILE = "/etc/ceph/ceph.conf"
ADMIN_KEYRING = "/etc/ceph/ceph.client.admin.keyring"

# `logging` MODULE CONFIG to use rsyslog ###
# 1. Set the application name (override the default `root` logger)
cc_logger = logging.getLogger("ceph_check")
cc_logger.setLevel(logging.DEBUG)
# 2. Set a Log handler to log to /var/log/messages
handler = logging.handlers.SysLogHandler(address='/dev/log')
# 3. Set up a log format
log_format = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
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

    def cc_condition(self):
        """
        Conditions for a successfull execution of `ceph_check`
        1. Ansible installed.
        2. Read-only access to the admin keyring.
        2. Passwordless SSH to the cluster nodes.
        """
        cc_logger.info("Calling check_ansible()")
        self.check_ansible()
        cc_logger.info("Calling check_keyring()")
        self.check_keyring()

    def check_ansible(self):
        try:
            cc_logger.info("Trying to load the ansible module")
            import ansible
            cc_logger.info("`ansible` module loaded, package installed.")
        except ImportError as err:
            cc_logger.exception(err)
            print("Exception - {0}".format(err))
            print("\nAnsible not installed. Install and re-run `ceph_check`.")
            sys.exit(-1)

    def check_keyring(self):
        """
        Check if a custom keyring exists
        """
        config_file = ConfigParser.SafeConfigParser()
        cc_logger.info("Reading '{0}'".format(CONF_FILE))
        config_file.read(self.conffile)
        cc_logger.info(
            "Checking for any custom keyrings in {0}".format(CONF_FILE))
        try:
            keyring_custom = config_file.get('global', 'keyring')
            cc_logger.info(
                "Found custom keyring at {0}".format(keyring_custom))
            self.keyring_permission(keyring_custom)
        except ConfigParser.NoOptionError:
            cc_logger.info(
                "No custom admin keyring specified in %s" % self.conffile)
            # cc_logger.info("Falling back to %s" % self.keyring)
            cc_logger.info("Falling back to {0}".format(self.keyring))
            cc_logger.info("Calling keyring_permission()")
            self.keyring_permission(self.keyring)

    def keyring_permission(self, keyring):
        """
        Check the existence and permission of the keyring
        """
        if os.path.isfile(self.keyring):
            cc_logger.info("{0} exists".format(self.keyring))
            if os.access(self.keyring, os.R_OK):
                cc_logger.info("{0} has read permissions".format(self.keyring))
                cc_logger.info("Calling ceph_report()")
                self.ceph_report()
            else:
                cc_logger.info("User {0} does not have read permissions\
                               for {1}".format(getpass.getuser(), self.keyring))
                print("User {0} does not have read permissions for {1}".format(
                    getpass.getuser(), self.keyring))
                cc_logger.info("Exiting!")
                print("\nExiting!\n")
                sys.exit(-1)
        else:
            cc_logger.info("Cannot find keyring at {0}".format(keyring))
            print("\nCannot find keyring at {0}".format(keyring))
            cc_logger.info("Exiting!")
            print("\nExiting!\n")
            sys.exit()

    def ceph_report(self):
        """[summary]

        [description]
        """
        report = "/tmp/report-" + time.strftime("%d%m%Y-%H%M%S")
        cc_logger.info("Generating cluster report")
        try:
            with open(report, "w") as output:
                subprocess.call(["/usr/bin/ceph", "report"],
                                stdout=output, stderr=subprocess.PIPE)
                cc_logger.info("Saved to %s" % report)
                cc_logger.info("Calling report_parse_summary()")
                self.report_parse_summary(report)
        except IOError:
            # It's very unlikely we'll hit this and exit here.
            print("Cannot write to /tmp, check permissions! Exiting!\n")
            cc_logger("Cannot create {0}".format(report))
            cc_logger.info("Exiting in ceph_report() - IOError")
            sys.exit(-1)

    def report_parse_summary(self, report):
        """
        Parse the ceph report and get cluster status

        """
        with open(report) as obj:
            json_obj = json.load(obj)
            cluster_status = json_obj['health']['overall_status']
            cc_logger.info("CLUSTER STATUS : {0}".format(cluster_status))
            print("\nceph_check REPORT:")
            print("-" * 18)
            print("CLUSTER STATUS : {0}".format(cluster_status))
            if cluster_status != "HEALTH_OK":
                # Print a general cluster summary, iterate over each object
                # within the "summary" dict, and print the 'value' for the
                # 'summary' key
                cc_logger.info("Cluster **not** HEALTHY!!")
                for i in json_obj['health']['summary']:
                    print(i['summary'])
                    cc_logger.info(i['summary'])
        cc_logger.info("Calling cluster_status()")
        self.cluster_status(report)

    def check_passwordless_ssh(self):
        """
        This is one of the three primary conditions for `ceph_check`.

        Check passwordless SSH access to the MON and OSD nodes
        """
        pass

    def cluster_status(self, report):
        """[summary]

        [description]

        Arguments:
            report {[type]} -- [description]
        """
        cc_logger.info("Starting to call helper functions")
        # Calling all helper functions irrespective of cluster status
        cc_logger.info("Calling mon_status_check()")
        self.mon_status_check(report)
        cc_logger.info("Calling osd_status_check()")
        self.osd_status_check(report)
        cc_logger.info("Calling pool_info()")
        self.pool_info(report)
        cc_logger.info("Calling pg_info()")
        self.pg_info(report)
        cc_logger.info("Calling ssh_check()")
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


if __name__ == "__main__":
    checker = CephCheck(CONF_FILE, ADMIN_KEYRING)
    try:
        checker.cc_condition()
    except Exception, err:
        cc_logger.exception(err)
        print("Exception - {0}".format(err))
        print("Hit Exception, check /var/log/messages for more info")
        sys.exit(-1)
