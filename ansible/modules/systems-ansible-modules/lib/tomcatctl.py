#!/usr/bin/env python
from ansible.module_utils.basic import AnsibleModule
import requests

DOCUMENTATION = """
---
module: tomcatctl
author:
    - "William Vanderlip-Mclean <wmclean@hy-vee.com>"
short_description: Control Tomcat applications
description:
    - Starts Applications
    - Stops Applications
    - Undeploys Applications
    - Redeploys Applications
    - Status of Applications
"""

EXAMPLES = """
- name: Start an Application
  tomcatctl:
    application: sdc
    username: admin
    password: passw0rd
    hostname: localhost
    action: start
"""


class Tomcatctl(object):
    def __init__(self, module):
        self.module = module
        self.application = module.params["application"]
        self.username = module.params["username"]
        self.password = module.params["password"]
        self.hostname = module.params["hostname"]
        self.action = module.params["action"]
        self.context = module.params["context"]
        self.session = module.params["session"]
        self.get_context = module.params["get_context"]
        self.get_status = module.params["get_status"]

    def get_info(self):
        response = self.session.get(
            "http://{}:8080/manager/text/list".format(self.hostname), timeout=180
        )

        for line in response.text.split("\n"):
            if self.application in line:
                if self.get_status:
                    result = "{} on {} is {}".format(
                        self.application, self.hostname, line.split(":")[1]
                    )
                elif self.get_context:
                    result = line.split(":")[3]
                else:
                    print("Provide bool get_status or get_context")
                return result

    def tomcat_action(self):
        response = self.session.get(
            "http://{}:8080/manager/text/{}?path=/{}".format(
                self.hostname, self.action, self.context
            ),
            timeout=480,
        )

        cmd_response = "{} on {}".format(response.text.rstrip(), self.hostname)
        return cmd_response

    def casestatement(self):
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)
        self.context = Tomcatctl.get_info(self)

        if self.action == "status":
            self.get_context = False
            self.get_status = True
            command_response = Tomcatctl.get_info(self)
        elif self.action == "restart":
            self.action = "stop"
            command_response = Tomcatctl.tomcat_action(self)
            self.action = "start"
            command_response = "{}\n{}".format(
                command_response, Tomcatctl.tomcat_action(self)
            )
        else:
            command_response = Tomcatctl.tomcat_action(self)

        return command_response.rstrip()


def main():
    argument_spec = dict(
        application=dict(type="str", required=True),
        username=dict(type="str", required=True),
        password=dict(type="str", required=True, no_log=True),
        hostname=dict(type="str", required=True),
        action=dict(
            choices=["status", "start", "stop", "restart", "reload", "undeploy"],
            type="str",
            required=True,
        ),
        context=dict(type="str", required=False),
        session=dict(required=False),
        get_context=dict(type="bool", required=False, default=True),
        get_status=dict(type="bool", required=False, default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=False,  # TODO: Support check mode in future version
    )

    result = {"failed": False, "changed": False}

    tomcatctl = Tomcatctl(module)

    process = tomcatctl.casestatement()

    result["output"] = process
    result.update(changed=True)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
