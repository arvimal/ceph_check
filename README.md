# ceph_check

Build Status
-------------

Build Status on Travis 
![Build status on Travis](https://img.shields.io/travis/arvimal/ceph_check.svg)


## Introduction

`ceph_check`, in short, is a reporting tool for RHCS/Ceph clusters.

* A distributed storage solution as Ceph has to be installed according to specific guide lines.

* This is important for optimal performance and ease of use. `ceph_check` intends to find unsupported or inoptimal configurations.

* `ceph_check` is mainly intended towards `Red Hat Ceph Storage` (RHCS) installations, but can be equally applied on upstream Ceph installations as well.

## Conditions:

`ceph_check` can be run from any node that fulfills the following points:

1. The node has to have `Ansible` installed.

2. The user executing the program has passwordless SSH access to the cluster nodes.

3. The user executing the program has at least `read access` to the Ceph Admin keyring.

## Features:

1. `ceph_check` will detect custom keyring locations, and use it appropriately. As a norm, any custom keyrings should be mentioned in `/etc/ceph/ceph.conf` for the Ceph cluster to work properly.

2. Checks the package versions on all the nodes in the Ceph cluster, and will report any descrepancies.

3. Reports the generic status of the Cluster.

4. Check if there is a custom cluster name. 'ceph' is the one that is supported right now.

5. Checks the number of placement groups in the pools, and suggests a proper value.

6. Reports if a single journal disk is being used for more than 6 OSD disks, since 6 is the suggested value.

7. Checks for colocated MONs and OSDs

8. Checks for RHCS Tech-preview features being used.

9. Checks for discrepancies in the CRUSH map.

10. `ceph_check` logs to /var/log/messages via `rsyslog`.

11. If the leader MON is not available, `ceph_check` will try to contact it three times each with an interval of 5, 10, and 15 seconds. If not able to contact within the said time period, it'll bail out.

## NOTE:

#### 1. subprocess and subprocess32 modules

`ceph_check` needs a few features of the `subprocess` module shipped in Python v3. But since `ceph_check` also targets OS versions running Python v2, we will need to use the module `subprocess32` which contains the much needed features backported to v2.

Refer [https://github.com/google/python-subprocess32](https://github.com/google/python-subprocess32)

* You'll need to install `gcc` and `python-devel`, before installing `subprocess32`.

~~~
# yum install gcc python-devel -y
~~~

* `subprocess32` can be installed using `pip`

~~~
# sudo pip install subprocess32
~~~

#### 2. Logging with rsyslog

`ceph_check` logs to rsyslog as of now.

It may move to the logger `ceph` uses in a later stage, or may use it's own log file as it initially did.

`rsyslog` dump logs which span multiple lines, as a single line. Even though `ceph_check` logs exceptions to /var/log/messages, it won't be formatted as python tracebacks would be.

For example, a ZeroDivisionError (or any other tracebacks) would look as:

~~~
Aug 21 19:00:30 rhel7 ceph_check: INFO: ####################
Aug 21 19:00:30 rhel7 ceph_check: INFO: Starting ceph_check
Aug 21 19:00:30 rhel7 ceph_check: INFO: Calling check_ansible()
Aug 21 19:00:30 rhel7 ceph_check: INFO: Trying to load the ansible module
Aug 21 19:00:30 rhel7 ceph_check: INFO: `ansible` module loaded, package installed.
Aug 21 19:00:30 rhel7 ceph_check: INFO: Calling check_keyring()
Aug 21 19:00:30 rhel7 ceph_check: INFO: Reading '/etc/ceph/ceph.conf'
Aug 21 19:00:30 rhel7 ceph_check: INFO: <--BUG--><--Cut here-->
Aug 21 19:00:30 rhel7 ceph_check: ERROR: integer division or modulo by zero#012Traceback (most recent call last):#012  File "ceph_check.py", line 266, in <module>#012    checker.cc_condition()#012  File "ceph_check.py", line 72, in cc_condition#012    self.check_keyring()#012  File "ceph_check.py", line 92, in check_keyring#012    1 / 0#012ZeroDivisionError: integer division or modulo by zero
~~~

This is due to rsyslog's behaviour of escaping newlines, tabs etc.. while logging them.

To fix this, add the following to `/etc/rsyslog.conf`, and restart `rsyslog`.

~~~
$EscapeControlCharactersOnReceive off
~~~

Logging should be as expected after this.

~~~
Traceback (most recent call last):
  File "ceph_check.py", line 266, in <module>
    checker.cc_condition()
  File "ceph_check.py", line 72, in cc_condition
    self.check_keyring()
  File "ceph_check.py", line 92, in check_keyring
    1 / 0
ZeroDivisionError: integer division or modulo by zero
~~~


