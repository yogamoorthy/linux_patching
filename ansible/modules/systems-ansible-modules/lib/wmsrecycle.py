#!/usr/bin/env python
from ansible.module_utils.basic import AnsibleModule

import subprocess
import os

DOCUMENTATION = """
---
module: wmsrecycle
author:
    - "William Vanderlip-Mclean <wmclean@hy-vee.com>"
short_description: Send action input to WMS
description:
    - Send action input to WMS
"""

EXAMPLES = """
- name: Do something to all apps
  wmsrecycle:
    application: all
    action: restart
    manh_home: /manh/apps/scope
    mip_name: mip
    mda_name: mda
    wm_name: wm
    lm_name: lm
    db_name: db

- name: Do something to wm
  wmsrecycle:
    application: wm
    action: restart
    manh_home: /manh/apps/scope
    wm_name: wm
"""


class WmsRecycle:
    def __init__(self, module):
        self.module = module
        self.local_scripts = module.params["local_scripts"]
        self.status_script = module.params["status_script"]
        self.app = module.params["application"]
        self.action = module.params["action"]
        self.manh_home = module.params["manh_home"]
        self.mip_name = module.params["mip_name"]
        self.mda_name = module.params["mda_name"]
        self.wm_name = module.params["wm_name"]
        self.lm_name = module.params["lm_name"]
        self.db_name = module.params["db_name"]
        self.manh_vars = {}
        self.status = []
        self.results = {}

    def run(self):
        self.manh_vars["manh_home"] = self.manh_home

        if self.app == "all":
            self.manh_vars["apps"] = [
                self.mip_name,
                self.mda_name,
                self.wm_name,
                self.lm_name,
                self.db_name,
            ]
        elif "mip" in self.app:
            self.manh_vars["apps"] = [self.mip_name]
        elif "mda" in self.app:
            self.manh_vars["apps"] = [self.mda_name]
        elif "wm" in self.app:
            self.manh_vars["apps"] = [self.wm_name]
        elif "lm" in self.app:
            self.manh_vars["apps"] = [self.lm_name]
        elif "db" in self.app:
            self.manh_vars["apps"] = [self.db_name]
        else:
            self.manh_vars["apps"] = [None]

        if self.action == "restart":
            self.action = "stop"
            self._run_action()
            self.action = "start"
            self._run_action()
        elif self.action == "status":
            self._status()
        else:
            self._run_action()

        return self.results

    def _status(self):
        for app in self.manh_vars["apps"]:
            command = "{}/{} {} {}".format(
                self.local_scripts, self.status_script, self.manh_vars["manh_home"], app
            )

            result = self.module.run_command(command)
            self.results[app] = {}
            self.results[app]["status"] = "{}".format(result[1].rstrip())

    def _run_action(self):
        for app in self.manh_vars['apps']:
            try:
                if 'wm' in app:
                    fnull = open(os.devnull, 'w')
                    rc = subprocess.call(
                        ['{}/{}/.sd/{}.sh'.format(self.manh_vars['manh_home'], app, self.action)],
                        stdout=fnull,
                        stderr=fnull
                    )
                    stdout = None
                else:
                    stdout = 'I met a condition'
                    result = subprocess.Popen(
                        ['{}/{}/.sd/{}.sh'.format(self.manh_vars['manh_home'], app, self.action)],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        preexec_fn=os.setpgrp
                    )
                    rc = result.wait()
                    stdout, stderr = result.communicate()

                if rc != 0:
                    self.results[app] = {}
                    self.results[app]['status'] = '{} {} - FAIL'.format(app, self.action)
                else:
                    self.results[app] = {}
                    self.results[app]['status'] = '{} {} - OK'.format(app, self.action)
            except OSError:
                self.results[app] = {}
                self.results[app]['status'] = '{} {} - FAIL'.format(app, self.action)


def main():
    argument_spec = dict(
        application=dict(type="str", required=True),
        action=dict(type="str", required=True),
        local_scripts=dict(type="str", required=False, default="/opt/hy-vee/scripts"),
        status_script=dict(type="str", required=False, default="wmsrecycle-status.sh"),
        manh_home=dict(type="str", required=False, default="/manh/apps/scope"),
        mip_name=dict(type="str", required=False, default="mip"),
        mda_name=dict(type="str", required=False, default="mda"),
        wm_name=dict(type="str", required=False, default="wm"),
        lm_name=dict(type="str", required=False, default="lm"),
        db_name=dict(type="str", required=False, default="db"),
    )

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    result = {"failed": False, "changed": False}
    obj_wmsrecycle = WmsRecycle(module)
    result["results"] = obj_wmsrecycle.run()

    result.update(changed=True)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
