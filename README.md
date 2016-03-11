# ceph_check 

ceph_check is a reporting tool, which checks a newly installed or an existing Ceph cluster, 
and report various unsupported or unoptimal configurations.  

An installation has to be according to the suggested guidelines, and checking/confirming 
this is a great way to prevent problems in the future.  

## Points worth considering:

1. This program should be run from the Ceph Administrator node, as the 'ceph' user.
2. If a custom username has been used to setup the Ceph cluster, use that account to execute the program.
3. The user running this script should have *read* permissions to the admin keyring.
4. SSH passwordless login should be setup for the user to the Ceph cluster nodes.

The above four points are the suggested requirements for an RHCS/Ceph installation, and hence can be expected 
to be present in a RHCS/Ceph cluster. 

## Features:

1. ceph_check will detect custom keyring locations, and use it appropriately. As a norm, any custom keyrings
should be mentioned in /etc/ceph/ceph.conf for the Ceph cluster to work properly.

2. Checks the package versions on all the nodes in the Ceph cluster, and will report any descrepancies.

3. Reports the generic status of the Cluster.

4. Check if there is a custom cluster name. 'ceph' is the one that is supported right now.

5. Checks the number of placement groups in the pools, and suggests a proper value.

6. Reports if a single journal disk is being used for more than 6 OSD disks, since 6 is the suggested value.

7. Checks for colocated MONs and OSDs

8. 
