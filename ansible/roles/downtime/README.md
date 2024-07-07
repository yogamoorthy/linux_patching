# downtime
Set downtime in Nagios

Requirement
------------
Host must exist in Nagios.

Required Variables
------------------

#### downtime_duration:
- Default value - '90'
- Possible values - 'any'
- Description - ***`This value must be set!`*** This value sets the amount (in minutes) the host is in downtime.

#### comment:
- Default value - 'Maintenance'
- Possible values - 'any'
- Description - ***`This value must be set!`*** This is the comment that will be applied when setting downtime.

Optional Variables
------------------

Dependencies
------------

Example Playbook
----------------
```yaml
---
- hosts: gk_qa
  gather_facts: true

- hosts: gk_qa
  gather_facts: false
  vars:
    downtime_duration: 60
    comment: "Server restart"
  roles:
    - role: downtime
...
```
License
-------

MIT

Author Information
------------------

Developled by - wmclean@hy-vee.com, Hy-Vee, inc.