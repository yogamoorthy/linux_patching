#!/usr/bin/env python
from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = """
---
module: mifports
author:
    - "William Vanderlip-Mclean <wmclean@hy-vee.com>"
short_description: Enable and Disable MIF Ports
description:
    - Enable Ports
    - Disable Ports
"""

EXAMPLES = """
- name: Disable MIF Ports - 2015
  mifports:
    user: cooldude
    password: coolpassword
    port: FilePollingListener:/manh/transfer/OM1/item/drop
    state: enable
    url: http://devmif17-v.hy-vee.net:5555/WmRoot/security-ports.dsp
    pkg: hyveeFilePolling

- name: Disable MIF Ports - 2017
  mifports:
    user: cooldude
    password: coolpassword
    port: FilePollingListener:/manh/transfer/OM1/item/drop
    state: enable
    url: http://devmif17-v.hy-vee.net:5555/WmRoot/security-ports.dsp
    verify: False
    pkg: hyveeFilePullingPorts
"""


class MifPorts:
    def __init__(self, module):
        self.module = module
        self.user = module.params["user"]
        self.password = module.params["password"]
        self.state = module.params["state"]
        self.port = module.params["port"]
        self.url = module.params["url"]
        self.pkg = module.params["pkg"]
        self.verify = module.params["verify"]
        self.result = {}

    def run(self):

        if self.state == "start" or self.state == "enable":
            self.state = "enable"
        elif self.state == "stop" or self.state == "disable":
            self.state = "disable"
        else:
            self.module.fail_json(
                msg="Requested State '{}' Not supported".format(self.state)
            )

        params = (
            ("listenerKey", self.port),
            ("operation", self.state),
            ("pkg", self.pkg),
        )

        response = requests.get(
            self.url, auth=(self.user, self.password), params=params, verify=self.verify
        )

        if response.status_code == 200:
            self.result["msg"] = "Port - {}".format(self.state)
        else:
            self.result["msg"] = "Port Failed- {}".format(self.state)

        return self.result


def main():
    argument_spec = dict(
        user=dict(type="str", required=True),
        password=dict(type="str", required=True),
        state=dict(type="str", required=True),
        port=dict(type="str", required=True),
        url=dict(type="str", required=True),
        verify=dict(type="str", required=False, default=True),
        pkg=dict(type="str", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    obj_MifPorts = MifPorts(module)
    response = obj_MifPorts.run()
    module.exit_json(**response)


if __name__ == "__main__":
    main()
