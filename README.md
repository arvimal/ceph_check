# ceph_check 

ceph_check is a reporting tool, which checks a newly installed or an existing Ceph cluster, 
and report various unsupported or unoptimal configurations.  

An installation has to be according to the suggested guidelines, and checking/confirming 
this is a great way to prevent problems in the future.  

Points worth considering:

1. This program should be run from the Ceph Administrator node, as the 'ceph' user.
2. If a custom username has been used to setup the Ceph cluster, use that account to execute the program.
3. The user running this script should have *read* permissions to the admin keyring.
4. SSH passwordless login should be setup for the user to the Ceph cluster nodes.

The above four points are the suggested requirements for an RHCS/Ceph installation, and hence can be expected 
to be present in a RHCS/Ceph cluster. 

1. ceph_check will detect custom keyring locations, and use it appropriately. If you are using a custom
admin keyring, you will need to mention that in /etc/ceph/ceph.conf.

2. The user running this script should have at least *read* permissions to the admin keyring.

3. 
ceph_check will detect custom keyring locations, and use it accordingly. The user running the script
should have read permissions though, which is of course the case if you want to execute any 'ceph' commands.



