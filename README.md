# ceph_check 

### Introduction

`ceph_check`, in short, is a reporting tool for RHCS/Ceph clusters.

* A distributed storage solution as Ceph has to be installed according to specific guide lines. 

* This is important for optimal performance and ease of use. `ceph_check` intends to find unsupported or inoptimal configurations.

* `ceph_check` is mainly intended towards `Red Hat Ceph Storage` (RHCS) installations, but can be equally applied on upstream Ceph installations as well.

## Conditions:

`ceph_check` can be run from any node that fulfills the following points:

1. The node has to have `Ansible` installed.

2. The user executing the program has passwordless SSH access to the cluster nodes.

3. The user executing the program has at least `read access` to the Ceph Admin keyring.

## NOTE:

`ceph_check()` needs Python v3. 

* RHEL7 and variants do not have v3 installed by default. Hence, you may want to install the package `python34` which ships Python v3.

~~~
# yum info python33
Loaded plugins: product-id, rhnplugin, search-disabled-repos, subscription-manager
Installed Packages
Name        : python33
Arch        : x86_64
Version     : 1.1
Release     : 13.el7
Size        : 0.0  
Repo        : installed
From repo   : rhel-x86_64-server-7-rhscl-1
Summary     : Package that installs python33
License     : GPLv2+
Description : This is the main package for python33 Software Collection.


# yum install -y python33-python
~~~

* Since python2.7 is the default version in RHEL7, `python33` will get installed to a custom path at `/opt/rh/python33`.

* To read the python3 shared libraries, set the PATH, LD_LIBRARY_PATH, and MANPATH variables.

~~~
# export PATH=/opt/rh/python33/root/usr/bin${PATH:+:${PATH}}
# export LD_LIBRARY_PATH=/opt/rh/python33/root/usr/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
# export MANPATH=/opt/rh/python33/root/usr/share/man:${MANPATH}
~~~

* After the environment variables are set, check for python3 versions. 

~~~
$ python<TAB>
python             python3            python3.3m         python-config
python2            python3.3          python3.3m-config  
python2.7          python3.3-config   python3-config     
~~~

* Execute `ceph_check` with `python3.3`.

~~~
$ python3 ceph_check.py
~~~

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

