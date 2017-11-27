#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ceph_check
# Vimal A.R | arvimal@yahoo.in

from __future__ import print_function
import time
import os
import sys
import json
import getpass
# import ConfigParser
import configparser
import logging
import logging.handlers
import tempfile

# We need the `timeout` feature in python3 subprocess module.
# This will need a `pip install subprocess32`.
try:
    import subprocess32
except ImportError:
    print("`ceph_check` requires `subprocess32` to function properly")
    print("`subprocess32` module required! Exiting.")
    sys.exit(-1)
"""
try:
    if os.name == 'posix' and sys.version_info[0] < 3:
        import subprocess32 as subprocess
    else:
        import subprocess
except ImportError:
    print("\n`ceph_check` requires `subprocess32` to function properly.\n")
    print("If you're on Python v2, use `pip` to install `subprocess32`.\n")
    print("# pip install subprocess32\n")
    print("Exiting!\n")
    sys.exit(-1)
"""
CONF_FILE = "/etc/ceph/ceph.conf"
ADMIN_KEYRING = "/etc/ceph/ceph.client.admin.keyring"

# `logging` MODULE CONFIG to use rsyslog ###
# 1. Set the application name (override the default `root` logger)
cc_logger = logging.getLogger("ceph_check")
cc_logger.setLevel(logging.DEBUG)
# 2. Set a Log handler to log to /var/log/messages
# NOTE: rsyslog won't handle multiline properly (exceptions here)
# Add `$EscapeControlCharactersOnReceive off` in /etc/rsyslog.conf to fix
handler = logging.handlers.SysLogHandler(address='/dev/log')
# 3. Set up a log format
log_format = logging.Formatter('%(name)s: %(levelname)-2s: %(message)s')
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
        Conditions for a successful execution of `ceph_check`
        1. Ansible installed.
        2. Read-only access to the admin keyring.
        2. Password-less SSH to the cluster nodes.
        """
        cc_logger.info("#" * 20)
        cc_logger.info("Starting ceph_check")
        cc_logger.info("Calling check_ansible()")
        self.check_ansible()
        cc_logger.info("Calling check_keyring()")
        self.check_keyring()

    def check_ansible(self):
        try:
            cc_logger.info("Trying to load the Ansible module")
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
            "Checking custom admin keyring in {0}".format(CONF_FILE))
        try:
            keyring_custom = config_file.get('global', 'keyring')
            cc_logger.info(
                "Found custom admin keyring at {0}".format(keyring_custom))
            self.keyring_permission(keyring_custom)
        except ConfigParser.NoOptionError:
            cc_logger.info(
                "No custom admin keyring specified in %s" % self.conffile)
            # cc_logger.info("Falling back to %s" % self.keyring)
            cc_logger.info("Trying {0}".format(self.keyring))
            if os.path.isfile(self.keyring):
                cc_logger.info("{0} exists".format(self.keyring))
                cc_logger.info("Calling keyring_permission()")
                self.keyring_permission(self.keyring)
            else:
                cc_logger.info(
                    "Cannot find admin keyring at {0}".format(self.keyring))
                print("Cannot find admin keyring at {0}".format(
                    self.keyring))
                print("\nThis is ideally hit when:\n")
                print("a. The admin keyring {0} is missing.".format(
                    self.keyring))
                print(
                    "b. A custom keyring exists but is not mentioned in {0}".format(CONF_FILE))
                print("\nFix the problem and re-run!")
                cc_logger.info("Exiting!")
                print("\nExiting!\n")
                sys.exit()

    def keyring_permission(self, keyring):
        """
        Check the existence and permission of the keyring
        """
        if os.access(self.keyring, os.R_OK):
            cc_logger.info("{0} has read permissions".format(self.keyring))
            cc_logger.info("Calling ceph_report()")
            self.ceph_report()
        else:
            cc_logger.info("User {0} does not have read permissions for {1}".format(
                getpass.getuser(), self.keyring))
            print("User {0} does not have read permissions for {1}".format(
                getpass.getuser(), self.keyring))
            cc_logger.info("Exiting!")
            print("\nExiting!\n")
            sys.exit(-1)

    def ceph_report(self):
        """
        Tries to generate a `ceph report`.
        """
        interval = [15, 10, 5]
        tries = 3
        temp_folder = tempfile.mkdtemp()
        report = temp_folder + "/" + "report-" + time.strftime("%d%m%Y-%H%M%S")
        cc_logger.info("Creating cluster report at {}".format(report))
        # import pdb
        # pdb.set_trace()
        with open(report, "w") as output:
            proc = subprocess32.Popen(["/usr/bin/ceph", "report"],
                                      stdout=output, stderr=subprocess32.PIPE)
            while tries:
                try:
                    # out/err gets populated if `communicate` succeeds
                    # If success, `out` won't contain anything,
                    # since `stdout` == report file,
                    # and `err` = `report <report-number>`
                    # In case of failure, `err` will contain :
                    # ~~~
                    # 7f3c38155700  0 monclient(hunting): authenticate timed
                    # out after 300
                    # 7f3c38155700  0 librados: client.admin authentication
                    # error (110)
                    # Connection timed out
                    # Error connecting to cluster: TimedOut
                    # ~~~
                    out, err = proc.communicate(timeout=interval[-1])
                    if "report" in err:
                        self.report_parse_summary(report)
                        # `report_parse_summary()` calls the helper funcs.
                        # Once finished, the control returns back here.
                        # It will un-necessarily logs failures.
                        # Hence calling `sys.exit()
                        sys.exit()
                except (subprocess32.TimeoutExpired):
                    cc_logger.info(
                        "Connection timed out, monitor host not reachable!")
                    print("\nConnection timed out, monitor host not reachable!")
                    tries -= 1
                    sleep_seconds = interval.pop()
                    cc_logger.info(
                        "Will retry after {0} seconds.".format(sleep_seconds))
                    print("Will retry after {0} seconds".format(sleep_seconds))
                    time.sleep(sleep_seconds)

            cc_logger.info(
                "Failing permanently. Not able to connect with the monitor")
            cc_logger.info("Check the monitor status!")
            print("\nFailing, not able to connect to the monitor!")

    def report_parse_summary(self, report):
        """
        Parse the ceph report and get cluster status
        """
        with open(report) as obj:
            json_obj = json.load(obj)
            cluster_status = json_obj['health']['overall_status']
            cc_logger.info("CLUSTER STATUS : {0}".format(cluster_status))
            print("\n\t- CLUSTER STATUS -\t")
            print("\n{0}".format(cluster_status))
            if cluster_status != "HEALTH_OK":
                cc_logger.info("Cluster **NOT** HEALTHY!!")
                print("\n\t- SUMMARY -\n")
                cc_logger.info("Cluster **NOT** HEALTHY!!")
                for i in json_obj['health']['summary']:
                    print(i['summary'])
                    cc_logger.info(i['summary'])
        cc_logger.info("Calling cluster_status()")
        self.cluster_status(report)

    def check_passwordless_ssh(self):
        """
        This is one of the three primary conditions for `ceph_check`.

        Check password-less SSH access to the MON and OSD nodes
        """
        pass

    def cluster_status(self, report):
        """
        Parse the report for further checks
        """
        cc_logger.info("Calling helper functions")
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
        self.check_passwordless_ssh()

    def mon_status_check(self, report):
        print("\n\t- MONITOR STATUS -\n")
        mon_list = []
        with open(report) as obj:
            json_obj = json.load(obj)
            print(
                "mon-map epoch    : {0}\n".format(str(json_obj['monmap']['epoch'])))
            print("-")
            for mon in json_obj['monmap']['mons']:
                print("Host name        : {0}".format(str(mon['name'])))
                print("Rank             : {0}".format(str(mon['rank'])))
                if str(mon['rank']) == "0":
                    print("Role             : {0}".format("Leader"))
                else:
                    print("Role             : {0}".format("Peon"))
                print("IP Address       : {0}".format(
                    str(mon['addr']).split(":")[0]))
                print("Port             : {0}".format(
                    str(mon['addr']).split(":")[1].split("/")[0]))
                print("-")
                cc_logger.info("{0}/{1}/{2}/{3}".format(str(mon['name']), str(
                    mon['rank']), str(mon['addr']), str(mon['addr']).split(":")[1].split("/")[0]))
                mon_list.append(str(mon['name']))
        cc_logger.info("MON List : {0}".format(mon_list))
        self.get_osd_and_mon_list(report)

    def get_osd_and_mon_list(self, report):
        """Get the list of MONs and OSDs from the report"""
        osds = {}
        with open(report) as obj:
            json_obj = json.load(obj)
            for osd in json_obj['osdmap']['osds']:
                osds[osd['osd']] = osd
                pass
        # return (mons, osds)

    def osd_status_check(self, report):
        print("\n\t- OSD STATUS -\n")
        with open(report) as obj:
            json_obj = json.load(obj)
            for i in json_obj:
                osd_id = "{0}".format(i['id'])
                print(osd_id)

    def pool_info(self, report):
        print("\n\t- POOL STATUS -\n")

    def pg_info(self, report):
        print("\n\t- PG STATUS -\n")


if __name__ == "__main__":
    checker = CephCheck(CONF_FILE, ADMIN_KEYRING)
    try:
        checker.cc_condition()
    except Exception as err:
        cc_logger.info("<--BUG--><--Cut here-->")
        cc_logger.exception(err, exc_info=True)
        print("Exception : {0}".format(err))
        print("Hit Exception. Check /var/log/messages for more detail.")
        sys.exit(-1)
