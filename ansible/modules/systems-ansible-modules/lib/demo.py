#!/usr/bin/env python
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = """
---
module: demo
author:
    - "Infra - Linux"
short_description: Demo Module
description:
    - Training tool for developing Ansible Modules
"""

EXAMPLES = """
- name: Test module
  demo:
    user: cooldude
"""

class Demo:
    def __init__(self, module):
        self.module = module
        self.user = module.params["user"]
        self.result = {}

    def run(self):
        self.result["msg"] = "Oh boy! {} is here!".format(self.user)

        return self.result

def main():
    argument_spec = dict(
        user=dict(type="str", required=True)
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    demo_obj  = Demo(module)
    response = demo_obj.run()
    module.exit_json(**response)


if __name__ == "__main__":
    main()
