#!/usr/bin/env python
from __future__ import print_function
from ansible.module_utils.basic import AnsibleModule

import sys
import requests
import datetime

DOCUMENTATION = """
---
module: nagctl
author:
    - "William Vanderlip-Mclean <wmclean@hy-vee.com>"
short_description: Set Downtime for Nagios XI
description:
    - Set Downtime for Nagios XI
updates:
    - duration: set in minutes
"""

EXAMPLES = """
- name: Set downtime
  nagctl:
    address: https://datacenterops.hy-vee.net
    apikey: nobnviubibvibiubebvhdhd
    action: set-downtime
    duration: 5
    host: gkprodsdc1-v
    servicegroups: ctl-dev
    comment: "Im shutting this boi down!"
    verify: False
"""


class NagCtl:
    def __init__(self, module):
        self.module = module
        self.apiKey = module.params["apikey"]
        self.hostName = module.params["host"]
        self.serviceGroups = module.params["servicegroups"]
        self.action = module.params["action"]
        self.downtimeDuration = module.params["duration"]
        self.comment = module.params["comment"]
        self.address = module.params["address"]
        self.verify = module.params["verify"]
        self.epoch = {}
        self.results = {}

    def run(self):
        self._bend_time()
        if self.hostName != "null":
            self._set_downtime_host()
        elif self.serviceGroups != "null":
            self._set_downtime_servicegroups()
        else:
            self.results["result"] = "Host or Service Group not defined"
        return self.results

    def _bend_time(self):
        time_int = self.downtimeDuration
        
        current_time = datetime.datetime.now()
        epoch_now = current_time.timestamp()
        epoch_future = epoch_now + (time_int * 60)

        self.epoch["start"] = epoch_now
        self.epoch["end"] = epoch_future

    def _set_downtime_host(self):
        url = self.address + "/nagiosxi/api/v1/system/scheduleddowntime"
        params = (
            ("apikey", self.apiKey),
            ("pretty", "1"),
        )
        data = {
            "comment": self.comment,
            "start": self.epoch["start"],
            "end": self.epoch["end"],
            "hosts[]": self.hostName,
        }

        response = requests.post(url, params=params, data=data, verify=self.verify)
        if "success" in response.text:
            self.results["result"] = "success"
        elif "error" in response.text:
            self.results["result"] = "error"

    def _set_downtime_servicegroups(self):
        url = self.address + "/nagiosxi/api/v1/system/scheduleddowntime"
        params = (
            ("apikey", self.apiKey),
            ("pretty", "1"),
        )
        data = {
            "comment": self.comment,
            "start": self.epoch["start"],
            "end": self.epoch["end"],
            "servicegroups[]": self.serviceGroups,
        }

        response = requests.post(url, params=params, data=data, verify=self.verify)
        if "success" in response.text:
            self.results["result"] = "success"
        elif "error" in response.text:
            self.results["result"] = "error"

def main():
    argument_spec = dict(
        apikey=dict(type="str", required=True),
        host=dict(type="str", required=False, default="null"),
        servicegroups=dict(type="str", required=False, default="null"), 
        action=dict(type="str", required=True),
        duration=dict(type="int", required=False, default=60),
        comment=dict(type="str", required=False, default="Ansible Is setting downtime"),
        address=dict(type="str", required=True),
        verify=dict(type="bool", required=False, default=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    result = {"failed": False, "changed": False}

    obj_NagCtl = NagCtl(module)

    result_info = obj_NagCtl.run()

    result["output"] = result_info
    result.update(changed=True)
    module.exit_json(**result)

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    main()
