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

