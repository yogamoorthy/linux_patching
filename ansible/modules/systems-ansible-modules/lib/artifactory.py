#!/usr/bin/env python3
from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = """
---
module: artifactory
author:
    - "William Vanderlip-Mclean <wmclean@hy-vee.com>"
short_description: Push file up
description:
    - push things
"""

EXAMPLES = """
- name: Push out content
  artifactory:
    operation: upload
    url: https://artifactory.prod.hy-vee.cloud/artifactory
    dest: wms-management-local/wsc-logs
    src: "tmp/path-to-file"
    user: "artifactory_user"
    password: "artifactory_password"
"""


class Artifactory:
    def __init__(self, module):
        self.module = module
        self.operation = module.params["operation"]
        self.user = module.params["user"]
        self.password = module.params["password"]
        self.url = module.params["url"]
        self.dest = module.params["dest"]
        self.src = module.params["src"]
        self.result = {}

    def run(self):
        if self.operation == "upload":
            self._upload()
            return self.result
        else:
            self.result["msg"] = "No Operation Input"
            return self.result

    def _upload(self):
        url = "{}/{}".format(self.url, self.dest)
        with open(self.src, "rb") as file:
            response = requests.put(url, auth=(self.user, self.password), data=file)

        self.result["msg"] = response.json()


def main():
    argument_spec = dict(
        operation=dict(type="str", required=True),
        user=dict(type="str", required=True),
        password=dict(type="str", required=True),
        url=dict(type="str", required=True),
        dest=dict(type="str", required=True),
        src=dict(type="str", required=True),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=False)

    obj_artifactory = Artifactory(module)
    response = obj_artifactory.run()
    module.exit_json(**response)


if __name__ == "__main__":
    main()
