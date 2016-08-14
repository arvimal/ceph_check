# ceph_check 

### Introduction

** `ceph_check`, in short, is a reporting tool for RHCS/Ceph clusters.

A distributed storage solution as Ceph has to be installed according to specific guide lines. 

This is important for optimal performance and ease of use. `ceph_check` intends to find unsupported or inoptimal configurations.

`ceph_check` is mainly intended towards RHCS installations, but can be equally applied on upstream Ceph installations as well.

## Conditions:

* `ceph_check` can be run from any node that fulfills the following points:

	1. The node has to have `Ansible` installed.

	2. The user executing the program has passwordless SSH access to the cluster nodes.

	3. The user executing the program has at least `read access` to the Ceph Admin keyring.

## Features:

1. ceph_check will detect custom keyring locations, and use it appropriately. 

As a norm, any custom keyrings should be mentioned in /etc/ceph/ceph.conf for the Ceph cluster to work properly.

2. Checks the package versions on all the nodes in the Ceph cluster, and will report any descrepancies.

3. Reports the generic status of the Cluster.

4. Check if there is a custom cluster name. 'ceph' is the one that is supported right now.

5. Checks the number of placement groups in the pools, and suggests a proper value.

6. Reports if a single journal disk is being used for more than 6 OSD disks, since 6 is the suggested value.

7. Checks for colocated MONs and OSDs

8. Checks for RHCS Tech-preview features being used.

9. Checks for discrepancies in the CRUSH map.

10. <And several others in the pipeline>

