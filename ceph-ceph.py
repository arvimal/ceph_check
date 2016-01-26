#!/usr/bin/env python

import rados
import rpm
# import subprocess
# import logging
# import argparse

conf = "/etc/ceph/ceph.conf"
ad_key = "/etc/ceph/ceph.client.admin.keyring"


class CephCheck(object):

    def __init__(self, conf=conf, ad_key=ad_key):
        self.conf = conf
        self.ad_key = ad_key

    def verify(self):
        # 1. Check for ceph-deploy rpm
        ts = rpm.TransactionSet()
        mi = ts.dbMatch()
        mi.pattern('name', rpm.RPMMIRE_GLOB, 'ceph-deploy')
        try:
            for h in mi:
                print("Checking ceph package installations.\n")
                print("%s-%s-%s" % (h['name'], h['version'], h['release']))
        except:
            print("Not able to find `ceph-deploy`")
        # 2. Check for ceph.conf
        if not self.conf:
            print("/etc/ceph/ceph.conf not found")
            print("Is this node part of the cluster?")


        self.verify_conf()

    def verify_conf(self):
        # if self.conf:
        print("\nVerifying configurations!")
        conf_file = open(self.conf)
        pass

    def connect(self):
        """Initialize the cluster connection"""
        try:
            cluster = rados.Rados(conffile='')
        except TypeError as e:
            raise e

        print("\nTrying to connect to the cluster..\n")

        try:
            cluster.connect()
        except Exception as e:
            print("Connection error : ", e)
            raise e
        finally:
            print("\nConnected to the cluster!\n")

    def help(self):
        """We help others"""
        print("\n")
        print("Usage : ")
        print("")

if __name__ == "__main__":
    ceph_check = CephCheck()
    ceph_check.verify()  # < add args, else print it'll take the default conf
