# ceph_check 

`ceph_check` is a reporting tool. 

It can be executed on a Ceph cluster, either newly installed or an existing one. It lets the end user know 
about various unsupported and unoptimal configurations.   

A distributed storage solution like Ceph has to be installed according to specific guidelines. This is important
for optimal performance and ease of use. 

A tool such as `ceph_check` can check and let the user know such configurations which can end up being pain points later.  

## Points worth considering:

1. This program is suggested to be run from the Admin node, as the `ceph` user.
2. Or execute it as the user with which `ceph-deploy` was executed. 
	- This is because SSH passwordless access would be available for such user accounts.
3. The user should have read permissions to the Admin keyring.
4. SSH passwordless access should be available to the cluster nodes.

All the above conditions would be met if this is executed as the user used to run 'ceph-deploy', 
from the Administrative node.

## Features:

1. ceph_check will detect custom keyring locations, and use it appropriately. As a norm, any custom keyrings
should be mentioned in /etc/ceph/ceph.conf for the Ceph cluster to work properly.

2. Checks the package versions on all the nodes in the Ceph cluster, and will report any descrepancies.

3. Reports the generic status of the Cluster.

4. Check if there is a custom cluster name. 'ceph' is the one that is supported right now.

5. Checks the number of placement groups in the pools, and suggests a proper value.

6. Reports if a single journal disk is being used for more than 6 OSD disks, since 6 is the suggested value.

7. Checks for colocated MONs and OSDs

8. Checks for RHCS Tech-preview features

